import os
import sys
import json
import traceback
import time
import concurrent.futures
import threading
import yaml
import pandas as pd
from datetime import datetime
from github import Github, Auth, UnknownObjectException, RateLimitExceededException
from dotenv import load_dotenv

# Variabile globale per aggregare i dati di tutti i team
all_dfs_teams = []

# ===================================================================
# SEZIONE: UTILS - AUTHENTICATION
# ===================================================================

def get_github_client(app_id, private_key_path, installation_id):
    """
    Autentica come GitHub App per una specifica installazione
    e restituisce un client PyGithub pronto all'uso.
    """
    try:
        with open(private_key_path, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        print(f"ERRORE CRITICO: File chiave privata non trovato a: {private_key_path}", file=sys.stderr)
        raise
    except Exception as e:
        print(f"ERRORE CRITICO: Impossibile leggere la chiave privata: {e}", file=sys.stderr)
        raise

    try:
        auth = Auth.AppAuth(app_id, private_key).get_installation_auth(installation_id)
        
        client = Github(auth=auth,  retry=3)
        
        limit = client.get_rate_limit().rate.remaining
        print(f"Autenticazione riuscita per ID {installation_id}. Rate limit iniziale: {limit}")
        
        return client
        
    except Exception as e:
        print(f"ERRORE: Autenticazione PyGithub fallita per l'installation ID {installation_id}.", file=sys.stderr)
        raise

# ===================================================================
# SEZIONE: UTILS - EXCEL WRITER
# ===================================================================

def get_output_filepath(output_dir):
    """
    Crea un percorso di file univoco per il report dei Team.
    """
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"github_TEAMS_report_{timestamp}.xlsx"
    return os.path.join(output_dir, filename)

def write_excel_report(df, output_file):
    """
    Scrive un singolo DataFrame in un file Excel.
    """
    print(f"\nScrittura del report Excel in: {output_file}")
    try:
        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            
            df.to_excel(writer, sheet_name='Report_Teams', index=False)
            
            # Auto-adatta larghezza colonne per leggibilità
            worksheet = writer.sheets['Report_Teams']
            for idx, col in enumerate(df.columns):
                series = df[col]
                max_len = max(
                    (series.astype(str).map(len).max() or 0),
                    len(str(col))
                ) + 2
                
                max_len = min(max_len, 75)
                worksheet.set_column(idx, idx, max_len)
                    
        print(f"Report Excel scritto con successo. Righe totali: {len(df)}")
        
    except Exception as e:
        print(f"ERRORE: Impossibile scrivere il file Excel. {e}")
        print(traceback.format_exc())

# ===================================================================
# SEZIONE: TEAM ANALYZER CLASS (Parallela)
# ===================================================================

class TeamAnalyzer:
    """
    Analizza i Team di un'organizzazione (gerarchia, membri, repo) 
    in parallelo, creando una riga per ogni utente/team.
    """
    
    def __init__(self, github_client: Github, organization_name=None, debug=False):
        if not github_client:
            raise ValueError("Per favore, fornisci un client PyGithub inizializzato.")
            
        self.g = github_client
        self.organization_name = organization_name
        self.debug = debug
        self._log(f"TeamAnalyzer inizializzato. Target: {self.organization_name}")

    def _log(self, message):
        """Funzione helper per stampare i log solo se il debug è attivo."""
        if self.debug:
            try:
                thread_id = threading.get_ident()
            except NameError:
                thread_id = "main"
            print(f"[DEBUG {thread_id}] {datetime.now().strftime('%H:%M:%S')} - {message}")

    # ===================================================================
    # METODO "WORKER" PER ELABORAZIONE TEAM (LOGICA PIVOT)
    # ===================================================================

    def _process_single_team(self, team):
        """
        Elabora UN singolo team. Questa funzione è eseguita in un thread.
        Recupera gerarchia, membri e repository.
        Restituisce una LISTA di dizionari (una riga per ogni utente nel team).
        """
        org_name = self.organization_name
        team_name = team.name
        self._log(f"Inizio analisi team: {org_name}/{team_name}")

        # Lista di righe (dizionari) da restituire per questo team
        team_rows_to_return = []

        try:
            # --- 1. Info Comuni (chiamate una sola volta per team) ---
            # Questi dati sono comuni a tutte le righe utente di questo team
            common_team_info = {
                'Organizzazione': org_name,
                'Team Name': team_name,
                'Team Slug': team.slug,
                'Parent Team': team.parent.name if team.parent else "N/A (Root)"
            }

            # --- 2. Repository e Permessi (chiamati una sola volta) ---
            repo_perms_list = []
            try:
                for repo in team.get_repos():
                    perms = repo.permissions
                    if perms.admin:
                        perm_level = 'admin'
                    elif perms.push:
                        perm_level = 'push'
                    elif perms.pull:
                        perm_level = 'pull'
                    else:
                        # Gestisce altri permessi (es. triage, maintain)
                        perm_level = 'custom/other'
                    
                    repo_perms_list.append(f"{repo.name}: {perm_level}")
            
            except Exception as e:
                self._log(f"ATTENZIONE: Impossibile ottenere i repo per il team {team_name}: {e}")
                repo_perms_list = ["Errore/Permessi insufficienti"]

            common_team_info['Repositories (Accesso)'] = " | ".join(repo_perms_list) if repo_perms_list else "Nessuno"

            # --- 3. Membri e Maintainer (Iterazione per Pivot) ---
            # Recupera le liste di utenti
            members_list = list(team.get_members(role='member'))
            maintainers_list = list(team.get_members(role='maintainer'))

            # Loop 1: Aggiungi righe per i Maintainer
            for user in maintainers_list:
                row = common_team_info.copy()
                row['User'] = user.login
                row['Role'] = 'maintainer'
                team_rows_to_return.append(row)

            # Loop 2: Aggiungi righe per i Member
            for user in members_list:
                row = common_team_info.copy()
                row['User'] = user.login
                row['Role'] = 'member'
                team_rows_to_return.append(row)
            
            # Caso: Team vuoto (nessun membro)
            if not members_list and not maintainers_list:
                row = common_team_info.copy()
                row['User'] = "Nessun membro"
                row['Role'] = "N/A"
                team_rows_to_return.append(row)
                
            self._log(f"Completata analisi team: {team_name} ({len(team_rows_to_return)} righe utente create)")
            
            # Restituisce la LISTA di righe
            return team_rows_to_return

        except Exception as e:
            print(f"ERRORE GENERALE durante l'analisi del team {team_name}: {e}")
            self._log(traceback.format_exc())
            # Restituisce una lista vuota in caso di errore
            return []

    # ===================================================================
    # METODO ORCHESTRATORE (TEAM)
    # ===================================================================

    def get_all_teams_details(self, max_workers=10):
        """
        Raccoglie i dettagli di TUTTI i team nell'organizzazione
        utilizzando un ThreadPoolExecutor.
        """
        self._log(f"\n--- Inizio Analisi Team per {self.organization_name} (Parallela) ---")
        
        try:
            org = self.g.get_organization(self.organization_name)
            all_teams = org.get_teams()
            total_teams = all_teams.totalCount
            print(f"Trovati {total_teams} team. Avvio di {max_workers} workers...")

        except UnknownObjectException:
            print(f"ERRORE: Organizzazione '{self.organization_name}' non trovata o non accessibile.")
            return None
        except Exception as e:
            print(f"ERRORE: Impossibile ottenere l'elenco dei team. {e}")
            self._log(traceback.format_exc())
            return None

        # Lista per i risultati (dizionari) di questa organizzazione
        organization_team_data = []
        team_count = 0

        # Inizia l'analisi parallela
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            
            future_to_team = {
                executor.submit(self._process_single_team, team): team
                for team in all_teams
            }
            
            for future in concurrent.futures.as_completed(future_to_team):
                team = future_to_team[future]
                team_name = team.name
                team_count += 1
                
                try:
                    # Ottieni la LISTA di righe (dizionari) dal thread
                    result_rows = future.result()
                    
                    if result_rows:
                        # Usa EXTEND per aggiungere tutte le righe utente
                        organization_team_data.extend(result_rows)
                        print(f"[{team_count}/{total_teams}] COMPLETATO: Team {team_name} ({len(result_rows)} righe utente trovate)")
                    else:
                        # Il worker ha restituito una lista vuota (errore)
                        print(f"[{team_count}/{total_teams}] COMPLETATO CON ERRORE: Team {team_name} (0 righe)")
                        
                except Exception as exc:
                    print(f"ERRORE CRITICO nel thread per il team {team_name}: {exc}")
                    self._log(traceback.format_exc())

        print(f"\n--- Analisi Team per {self.organization_name} completata ---")

        if not organization_team_data:
            print("Nessun dato dei team è stato raccolto.")
            return pd.DataFrame()
            
        print(f"Totale righe TEAM raccolte per {self.organization_name}: {len(organization_team_data)}")
        
        return pd.DataFrame(organization_team_data)

# ===================================================================
# SEZIONE: MAIN SCRIPT LOGIC
# ===================================================================

def load_config():
    """Load configurations from .env"""
    print("Loading configuration...")
    load_dotenv()
    
    config = {
        "app_id": os.getenv("GITHUB_APP_ID"),
        "private_key_path": os.getenv("GITHUB_PRIVATE_KEY_PATH"),
        "debug": os.getenv("DEBUG_MODE", "False").lower() == "true",
        "output_dir": os.getenv("OUTPUT_DIR", "output"),
        "max_workers": int(os.getenv("MAX_WORKERS", "10")) # Controlla il parallelismo
    }
    
    if not all([config["app_id"], config["private_key_path"]]):
        print("ERRORE: GITHUB_APP_ID e GITHUB_PRIVATE_KEY_PATH")
        print("devono essere impostati nel file .env.")
        sys.exit(1)
        
    print(f"Configurazione caricata. Workers paralleli: {config['max_workers']}")
    return config

def main():
    """Main script function."""
    global all_dfs_teams # Usa la lista globale
    
    try:
        config = load_config()
        
        # --- Carica le installazioni da 'installations.yaml' ---
        installations_file = 'installations.yaml'
        try:
            with open(installations_file, 'r') as f:
                installations_data = yaml.safe_load(f)
                all_installations = installations_data.get('installations', [])
        except FileNotFoundError:
            print(f"Errore: '{installations_file}' non trovato.", file=sys.stderr)
            print("Esegui prima 'find_installations.py' per generare questo file.", file=sys.stderr)
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"Errore nel parsing di '{installations_file}': {e}", file=sys.stderr)
            sys.exit(1)
            
        if not all_installations:
            print("Nessuna installazione trovata in 'installations.yaml'. Uscita.")
            sys.exit(0)
        
        print(f"Trovate {len(all_installations)} organizzazioni. Inizio ciclo...")
        
        # --- Itera su ogni organizzazione ---
        for inst in all_installations:
            org_name = inst.get("account_login")
            inst_id = inst.get("installation_id")
            
            if not org_name or not inst_id:
                print(f"Skipping invalid installation entry: {inst}")
                continue
                
            print(f"\n--- Elaborazione Organizzazione: {org_name} (ID: {inst_id}) ---")
            
            try:
                # 1. Ottieni il client GitHub autenticato
                client = get_github_client(
                    app_id=config["app_id"],
                    private_key_path=config["private_key_path"],
                    installation_id=inst_id
                )
                
                # 2. Inizializza l'analyzer
                analyzer = TeamAnalyzer(
                    github_client=client,
                    organization_name=org_name,
                    debug=config["debug"],
                )
                
                # 3. Esegui l'analisi dei team (parallela)
                df = analyzer.get_all_teams_details(
                    max_workers=config["max_workers"]
                )
                
                # 4. Aggiungi il DataFrame (se non vuoto) alla lista aggregata
                if df is not None and not df.empty:
                    print(f"Dati TEAM raccolti con successo per {org_name}.")
                    all_dfs_teams.append(df)
                elif df is None:
                    print(f"Analisi TEAM fallita per {org_name}.")
                else:
                    print(f"Nessun dato TEAM trovato per {org_name}.")
            
            except Exception as e:
                print(f"❌ FALLITO processamento organizzazione {org_name}: {e}")
                if config["debug"]:
                    traceback.print_exc()
        
        print("\n--- Tutte le organizzazioni sono state processate ---")
        
        # --- BLOCCO FINALE: Scrive un singolo file aggregato ---
        if not all_dfs_teams:
            print("Nessun dato dei team raccolto. Nessun report generato.")
            sys.exit(0)
            
        print(f"\nAggregazione dati Team da {len(all_dfs_teams)} organizzazioni...")
        combined_df = pd.concat(all_dfs_teams, ignore_index=True)
        
        # Scrive il file Excel
        output_file = get_output_filepath(config["output_dir"]) 
        write_excel_report(combined_df, output_file)

    except Exception as e:
        print(f"\n❌ ERRORE CRITICO DELLO SCRIPT: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
