
import os
import sys
import json
import traceback
import yaml
import pandas as pd
from dotenv import load_dotenv
from commons.auth import get_github_client
from commons.excel_writer import get_output_filepath, write_excel_report
import traceback
import concurrent.futures
import pandas as pd
from datetime import datetime
from github import Github,  UnknownObjectException, RateLimitExceededException
import threading

class RepoAnalyzer:
    """
    Analizza sia i dettagli dell'Organizzazione che i suoi Repository in parallelo.
    """
    
    def __init__(self, github_client: Github, organization_name=None, debug=False):
        if not github_client:
            raise ValueError("Per favore, fornisci un client PyGithub inizializzato.")
            
        self.g = github_client
        self.organization_name = organization_name
        self.debug = debug
        self._log(f"RepoAnalyzer inizializzato. Debug: {self.debug}")
        self._log(f"Target Organizzazione: {self.organization_name or 'Tutti i repo accessibili'}")

    def _log(self, message):
        """Funzione helper per stampare i log solo se il debug è attivo."""
        if self.debug:
            try:
                thread_id = threading.get_ident()
            except NameError:
                thread_id = "main"
            print(f"[DEBUG {thread_id}] {datetime.now().strftime('%H:%M:%S')} - {message}")

    # --- Inizio Metodi di Raccolta Dati REPOSITORY ---


    def _get_team_permissions(self, repo):
        self._log(f"Estrazione permessi team per {repo.full_name}...")
        teams_data = []
        try:
            teams = repo.get_teams()
            if teams.totalCount == 0:
                self._log("Nessun team trovato.")
                return "Nessun Team"

            for team in teams:
                permission = repo.get_team_permission(team) 
                teams_data.append(f"{team.name}: {permission}")
                self._log(f" - Team {team.name}: permesso {permission}")
                
        except UnknownObjectException:
            self._log("Errore: Non repo di Organizzazione o risorsa sconosciuta.")
            return "N/A (Non Organizzazione)"
        except Exception as e:
            print(f"Errore estrazione team per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return "Errore API/Permessi"
        return " | ".join(teams_data)

    def count_files_in_branch(self, repo, branch_name):
        
        self._log(f"Conteggio file nel branch {branch_name}...")
        try:
            commit_sha = repo.get_branch(branch_name).commit.sha
            tree = repo.get_git_tree(commit_sha, recursive=True)
            count = sum(1 for element in tree.tree if element.type == 'blob')
            self._log(f" - Trovati {count} file.")
            return count
        except Exception as e:
            print(f" - Errore conteggio file nel branch {branch_name} per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return "Errore/Non disponibile"
    
    def check_readme(self, repo):
        
        self._log("Verifica README...")
        try:
            repo.get_readme()
            self._log(" - README trovato.")
            return "Sì"
        except UnknownObjectException as e:
            if "empty" in str(e).lower():
                self._log(" - Repository vuoto.")
                return "No (Repo vuoto)" 
            else:
                self._log(" - README NON trovato.")
                return "No"
        except Exception as e:
            print(f" - Errore verifica README per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return "Errore API"
            
    def _calculate_avg_pr_merge_time(self, repo, limit=50):
        
        self._log(f"Calcolo tempo medio merge (ultime {limit} PR)...")
        merge_times = []
        try:
            pulls = repo.get_pulls(state='closed', sort='updated', direction='desc')
            for pr in pulls[:limit]:
                if pr.merged_at:
                    time_to_merge = pr.merged_at - pr.created_at
                    merge_times.append(time_to_merge.total_seconds())
            
            if merge_times:
                avg_seconds = sum(merge_times) / len(merge_times)
                avg_days = avg_seconds / (60 * 60 * 24)
                self._log(f" - Tempo medio: {avg_days:.2f} giorni.")
                return f"{avg_days:.2f} giorni"
            
            self._log(" - Nessuna PR mergiata trovata.")
            return "N/A (Nessuna PR mergiata)"
        except Exception as e:
            print(f" - Errore calcolo tempo merge per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return "Errore API"

    def _get_branch_protection_status(self, repo):
        
        default_branch = repo.default_branch
        self._log(f"Verifica protezione branch di default ({default_branch})...")
        try:
            branch = repo.get_branch(default_branch)
            branch.get_protection() 
            self._log(" - Protezione branch ATTIVA.")
            return "Sì"
        except UnknownObjectException:
            self._log(" - Branch non protetto o non esiste.")
            return "No (Non protetto)"
        except Exception as e:
            print(f" - Errore permessi protezione branch per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return f"Errore Permessi ({default_branch})"

    def _get_active_webhooks_count(self, repo):
        
        self._log("Conteggio webhooks attivi...")
        try:
            count = len(list(repo.get_hooks()))
            self._log(f" - Trovati {count} webhooks.")
            return count
        except Exception as e:
            print(f" - Errore conteggio webhooks per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return "Errore/Non disponibile"
            
    def _get_license_info(self, repo):
        
        self._log("Estrazione licenza...")
        try:
            license_info = repo.get_license()
            name = license_info.license.spdx_id or license_info.license.name
            self._log(f" - Licenza trovata: {name}")
            return name
        except UnknownObjectException:
            self._log(" - Nessuna Licenza Trovata.")
            return "Nessuna Licenza Trovata"
        except Exception as e:
            print(f" - Errore estrazione licenza per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return "Errore API"

    def _check_dependabot(self, repo):
        
        self._log("Verifica stato Dependabot...")
        try:
            repo.get_contents(".github/dependabot.yml")
            self._log(" - Dependabot configurato via file.")
            return "Sì (configurazione trovata)"
        except UnknownObjectException:
            try:
                if repo.get_vulnerability_alert():
                    self._log(" - Dependabot attivo (alert trovati).")
                    return "Sì (alert attivi)"
                else:
                    self._log(" - Dependabot non trovato (alert disattivi).")
                    return "No"
            except Exception as e:
                self._log(f" - Errore verifica alert Dependabot: {e}")
                return "No (Errore verifica alert)"
        except Exception as e:
            self._log(f" - Errore generico Dependabot: {e}")
            return "Errore API"

    def _check_sonar_codacy(self, repo):
        
        self._log("Verifica stato Codacy/SonarQube...")
        try:
            repo.get_contents("sonar-project.properties")
            self._log(" - SonarQube configurato.")
            return "Sì (SonarQube)"
        except UnknownObjectException:
            try:
                repo.get_contents(".codacy.yml")
                self._log(" - Codacy configurato.")
                return "Sì (Codacy)"
            except UnknownObjectException:
                self._log(" - SonarQube/Codacy non trovato.")
                return "No"
            except Exception as e:
                 self._log(f" - Errore verifica Codacy: {e}")
                 return "Errore API"
        except Exception as e:
            self._log(f" - Errore verifica Sonar: {e}")
            return "Errore API"

    def _get_branches_and_file_counts(self, repo):
        
        self._log("Estrazione branch e conteggio file...")
        branches_list = []
        files_per_branch_details = []
        try:
            for branch in repo.get_branches():
                branches_list.append(branch.name)
                file_count = self.count_files_in_branch(repo, branch.name) 
                files_per_branch_details.append(f"{branch.name}: {file_count}")
            self._log(f" - Branch estratti: {branches_list}")
        except Exception as e:
            print(f" - Errore estrazione branch per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            pass
        return ", ".join(branches_list), " | ".join(files_per_branch_details)

    def _get_collaborators(self, repo):
        
        self._log("Estrazione collaboratori diretti...")
        collaborators_read = []
        collaborators_write = []
        try:
            for user in repo.get_collaborators():
                permissions = user.permissions
                if permissions.push or permissions.admin:
                    collaborators_write.append(user.login)
                elif permissions.pull:
                    collaborators_read.append(user.login)
            self._log(f" - Scrittura: {len(collaborators_write)} utenti. Lettura: {len(collaborators_read)} utenti.")
        except Exception as e:
            print(f" - Errore estrazione collaboratori per {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return "Errore/Permessi", ["Errore/Permessi"]
        
        read_str = ", ".join(collaborators_read) if collaborators_read else "Nessuno"
        write_list = collaborators_write if collaborators_write else ["Nessun Collaboratore Diretto"]
        return read_str, write_list
    
    # --- Fine Metodi di Raccolta Dati REPOSITORY ---

    # ===================================================================
    # NUOVO METODO: Raccolta Dati ORGANIZZAZIONE
    # ===================================================================

    def get_organization_details(self):
        """
        Raccoglie informazioni a livello di organizzazione, inclusi
        membri e loro ruoli.
        """
        self._log(f"Recupero dettagli per l'organizzazione {self.organization_name}")
        
        try:
            org = self.g.get_organization(self.organization_name)
        except Exception as e:
            print(f"ERRORE: Impossibile ottenere l'oggetto organizzazione {self.organization_name}: {e}")
            return None

        # Raccogli info generali
        try:
            two_factor_enabled = org.two_factor_requirement_enabled
        except Exception:
            two_factor_enabled = "Errore/Permessi"
            
        try:
            # Richiede permessi di admin
            billing_email = org.billing_email 
        except Exception:
            billing_email = "N/A (Permessi insufficienti)"

        org_details_base = {
            'Organizzazione': org.login,
            '2FA Obbligatoria': "Sì" if two_factor_enabled else "No",
            'Email Billing': billing_email,
            'Default Repo Permission': org.default_repository_permission,
            'Totale Repo (Privati)': org.total_private_repos,
            'Totale Repo (Pubblici)': org.public_repos
        }
        
        members_data = []
        
        # Raccogli Amministratori
        try:
            self._log("Recupero Admins...")
            for member in org.get_members(role='admin'):
                row = org_details_base.copy()
                row.update({
                    'User': member.login,
                    'Role': 'Admin'
                })
                members_data.append(row)
        except Exception as e:
            print(f"ATTENZIONE: Impossibile recuperare gli Admin per {org.login}: {e}")
            self._log(traceback.format_exc())

        # Raccogli Membri
        try:
            self._log("Recupero Members...")
            for member in org.get_members(role='member'):
                row = org_details_base.copy()
                row.update({
                    'User': member.login,
                    'Role': 'Member'
                })
                members_data.append(row)
        except Exception as e:
            print(f"ATTENZIONE: Impossibile recuperare i Membri per {org.login}: {e}")
            self._log(traceback.format_exc())
            
        if not members_data:
            self._log("Nessun membro trovato o errore permessi.")
            # Aggiungi almeno una riga con i dati dell'org
            members_data.append(org_details_base)
            
        return pd.DataFrame(members_data)

    # ===================================================================
    # METODO "WORKER" PER ELABORAZIONE REPOSITORY
    # ===================================================================
    
    def _process_single_repo(self, repo, output_fields):
        """
        Elabora UN singolo repository. Questa funzione è eseguita in un thread.
        """
        try:
            self._log(f"Inizio analisi: {repo.full_name}...")
            
            # --- 1. DATI DEI COLLABORATORI ---
            read_collabs_str, write_collabs_list = self._get_collaborators(repo)

            # --- 2. DIZIONARIO DATI COMUNI ---
            common_repo_info = {}

            if "Nome Repo" in output_fields:
                common_repo_info["Nome Repo"] = repo.full_name
            if "Descrizione" in output_fields:
                common_repo_info["Descrizione"] = repo.description if repo.description else ""
            if "Licenza" in output_fields:
                common_repo_info["Licenza"] = self._get_license_info(repo)
            if "Archiviata" in output_fields:
                common_repo_info["Archiviata"] = "Sì" if repo.archived else "No"
            if "Data Ultimo Commit" in output_fields:
                common_repo_info["Data Ultimo Commit"] = repo.pushed_at.strftime("%Y-%m-%d") if repo.pushed_at else "N/A"
            if "Stato README" in output_fields:
                common_repo_info["Stato README"] = self.check_readme(repo)
            if "Branch Default" in output_fields:
                common_repo_info["Branch Default"] = repo.default_branch
            if "Stato Protezione Branch Default" in output_fields:
                common_repo_info["Stato Protezione Branch Default"] = self._get_branch_protection_status(repo)
            if "Permessi Lettura (Collaboratori Diretti)" in output_fields:
                common_repo_info["Permessi Lettura (Collaboratori Diretti)"] = read_collabs_str
            if "Permessi per Team (Team: Livello)" in output_fields:
                common_repo_info["Permessi per Team (Team: Livello)"] = self._get_team_permissions(repo)
            if "Numero Webhooks Attivi" in output_fields:
                common_repo_info["Numero Webhooks Attivi"] = self._get_active_webhooks_count(repo)
            if "Tempo Medio Merge PR (Ult. 50)" in output_fields:
                common_repo_info["Tempo Medio Merge PR (Ult. 50)"] = self._calculate_avg_pr_merge_time(repo)
            if "Numero Issue Aperte" in output_fields:
                common_repo_info["Numero Issue Aperte"] = repo.open_issues_count
            if "Numero Pull Request Aperte" in output_fields:
                common_repo_info["Numero Pull Request Aperte"] = repo.get_pulls(state='open').totalCount
            if "Dependabot Attivo" in output_fields:
                common_repo_info["Dependabot Attivo"] = self._check_dependabot(repo)
            if "Top Contributori" in output_fields:
                common_repo_info["Top Contributori"] = ", ".join([c.login for c in repo.get_contributors()[:100]])
            if "Linguaggi Principali" in output_fields:
                common_repo_info["Linguaggi Principali"] = ", ".join(list(repo.get_languages().keys()))
            if "Codacy/SonarQube Attivo" in output_fields:
                common_repo_info["Codacy/SonarQube Attivo"] = self._check_sonar_codacy(repo)
            if "Branch (Nomi)" in output_fields or "Numero File per Branch" in output_fields:
                branches, files = self._get_branches_and_file_counts(repo)
                if "Branch (Nomi)" in output_fields:
                    common_repo_info["Branch (Nomi)"] = branches
                if "Numero File per Branch" in output_fields:
                    common_repo_info["Numero File per Branch"] = files
            if "Dimensione (MB)" in output_fields:
                common_repo_info["Dimensione (MB)"] = f"{repo.size / 1024:.2f}"

            # --- 3. ITERAZIONE SUI "WRITERS" ---
            repo_rows_to_return = []
            
            for each_writer in write_collabs_list:
                repo_info = common_repo_info.copy()
                if "Permessi Scrittura (Collaboratori Diretti)" in output_fields:
                    repo_info["Permessi Scrittura (Collaboratori Diretti)"] = each_writer
                repo_rows_to_return.append(repo_info)
                
            self._log(f"Dati raccolti per {repo.full_name} ({len(repo_rows_to_return)} righe create)")
            return repo_rows_to_return
            
        except RateLimitExceededException:
            print(f"\nFATAL: Limite di Rate API GitHub superato (il worker si ferma) per {repo.full_name}.")
            self._log(traceback.format_exc())
            return None
        except Exception as e:
            print(f"ERRORE GENERALE durante l'analisi di {repo.full_name}: {e}")
            self._log(traceback.format_exc())
            return []

    # ===================================================================
    # METODO ORCHESTRATORE (REPOSITORY)
    # ===================================================================

    def get_repo_details(self, output_fields: list, max_workers=10):
        """
        Raccoglie i dettagli dei REPOSITORY in parallelo.
        """
        self._log(f"output_fields: {output_fields}")
        if not output_fields:
            print("ATTENZIONE: Nessun campo di output specificato per i repo. Il report sarà vuoto.")
            return pd.DataFrame()

        self._log(f"\n--- Inizio Analisi Repository (Modalità Parallela: {max_workers} workers) ---")
        
        try:
            if self.organization_name:
                self._log(f"Accesso all'organizzazione: {self.organization_name}...")
                org = self.g.get_organization(self.organization_name)
                repositories = org.get_repos()
                total_repos = repositories.totalCount
            else:
                self._log("Accesso a tutti i repository visibili dall'installazione...")
                repositories = self.g.get_user().get_repos()
                total_repos = repositories.totalCount
            
            print(f"Trovati {total_repos} repository. Avvio di {max_workers} workers...")
        
        except UnknownObjectException:
            print(f"ERRORE: Organizzazione '{self.organization_name}' non trovata o non accessibile.")
            return None
        except Exception as e:
            print(f"ERRORE: Impossibile ottenere l'elenco dei repository. {e}")
            self._log(traceback.format_exc())
            return None

        internal_repos_data = []
        repo_count = 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_repo = {
                executor.submit(self._process_single_repo, repo, output_fields): repo
                for repo in repositories
            }
            
            for future in concurrent.futures.as_completed(future_to_repo):
                repo = future_to_repo[future]
                repo_name = repo.full_name
                repo_count += 1
                
                try:
                    result_rows = future.result()
                    
                    if result_rows is None:
                        print(f"\nFATAL: Rate Limit rilevato su {repo_name}. Annullamento di tutti i task futuri...")
                        executor.shutdown(wait=False, cancel_futures=True) 
                        break
                        
                    if result_rows:
                        internal_repos_data.extend(result_rows)
                        print(f"[{repo_count}/{total_repos}] COMPLETATO: {repo_name} ({len(result_rows)} righe aggiunte)")
                    else:
                        print(f"[{repo_count}/{total_repos}] COMPLETATO CON ERRORE: {repo_name} (0 righe aggiunte)")
                        
                except Exception as exc:
                    print(f"ERRORE CRITICO nel thread per {repo_name}: {exc}")
                    self._log(traceback.format_exc())

        print(f"\n--- Analisi Repository per {self.organization_name} completata ---")

        if not internal_repos_data:
            print("Nessun dato del repository è stato raccolto per questa organizzazione.")
            return pd.DataFrame()
            
        print(f"Totale righe REPO raccolte per {self.organization_name}: {len(internal_repos_data)}")
        
        df = pd.DataFrame(internal_repos_data)
        present_fields = [f for f in output_fields if f in df.columns]
        df = df[present_fields]
        
        return df


# Variabili globali per aggregare i dati
all_dfs_repos = []
all_dfs_orgs = []

def load_config():
    """Load configurations from .env and output_fields.json"""
    print("Loading configuration...")
    load_dotenv()
    
    config = {
        "app_id": os.getenv("GITHUB_APP_ID"),
        "private_key_path": os.getenv("GITHUB_PRIVATE_KEY_PATH"),
        "installation_id": os.getenv("GITHUB_INSTALLATION_ID"), # Can be None
        "org_name": os.getenv("GITHUB_ORGANIZATION_NAME"), # Can be None
        "debug": os.getenv("DEBUG_MODE", "False").lower() == "true",
        "output_dir": os.getenv("OUTPUT_DIR", "output"),
        "output_fields": os.getenv("EXCEL_FIELDS", "output"),
        "max_workers": 10
    }
    
    # --- MODIFIED VALIDATION ---
    # installation_id is no longer required here.
    # If it's missing, we will fetch all installations.
    if not all([config["app_id"], config["private_key_path"]]):
        print("ERROR: GITHUB_APP_ID and GITHUB_PRIVATE_KEY_PATH")
        print("must be set in the .env file.")
        sys.exit(1)
        
    # Load output fields
    try:
        with open("config/output_fields.json", 'r') as f:
            config["output_fields"] = json.load(f).get("fields", [])
        if not config["output_fields"]:
            print("WARNING: 'config/output_fields.json' is empty. The report will contain no columns.")
    except FileNotFoundError:
        print("ERROR: File 'config/output_fields.json' not found.")
        print("Please ensure the file exists and contains a list of 'fields'.")
        sys.exit(1)
    except json.JSONDecodeError:
        print("ERROR: Could not parse 'config/output_fields.json'. Check JSON syntax.")
        sys.exit(1)
        
    print("Configuration loaded successfully.")
    return config

def main():
    """Main script function."""
    global all_dfs_repos, all_dfs_orgs # Usa le liste globali
    
    try:
        config = load_config()
        
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
        
        print(f"Trovate {len(all_installations)} organizzazioni in '{installations_file}'. Inizio ciclo...")
        
        for inst in all_installations:
            org_name = inst.get("account_login")
            inst_id = inst.get("installation_id")
            
            if not org_name or not inst_id:
                print(f"Skipping invalid installation entry: {inst}")
                continue
                
            print(f"\n--- Elaborazione Organizzazione: {org_name} (ID: {inst_id}) ---")
            
            try:
                client = get_github_client(
                    app_id=config["app_id"],
                    private_key_path=config["private_key_path"],
                    installation_id=inst_id
                )
                
                analyzer = RepoAnalyzer(
                    github_client=client,
                    organization_name=org_name,
                    debug=config["debug"],
                )
                
                # --- 1. Esegui analisi ORGANIZZAZIONE ---
                print(f"Avvio analisi a livello di Organizzazione per {org_name}...")
                org_df = analyzer.get_organization_details()
                if org_df is not None and not org_df.empty:
                    print(f"Dati ORGANIZZAZIONE raccolti per {org_name}.")
                    all_dfs_orgs.append(org_df)
                else:
                    print(f"Nessun dato a livello Organizzazione trovato per {org_name}.")

                # --- 2. Esegui analisi REPOSITORY (parallela) ---
                print(f"Avvio analisi a livello di Repository per {org_name}...")
                repo_df = analyzer.get_repo_details(
                    output_fields=config["output_fields"],
                    max_workers=config["max_workers"]
                )
                
                if repo_df is not None and not repo_df.empty:
                    print(f"Dati REPOSITORY raccolti per {org_name}.")
                    all_dfs_repos.append(repo_df)
                elif repo_df is None:
                    print(f"Analisi REPOSITORY fallita per {org_name}.")
                else:
                    print(f"Nessun dato REPOSITORY trovato per {org_name}.")
            
            except Exception as e:
                print(f"❌ FALLITO processamento organizzazione {org_name}: {e}")
                if config["debug"]:
                    traceback.print_exc()
        
        print("\n--- Tutte le organizzazioni sono state processate ---")
        
        # --- BLOCCO FINALE: Scrive un singolo file aggregato con 2 fogli ---
        
        dfs_to_write = {}
        
        if not all_dfs_repos and not all_dfs_orgs:
            print("Nessun dato raccolto da nessuna organizzazione. Nessun report generato.")
            sys.exit(0)
            
        if all_dfs_orgs:
            print(f"\nAggregazione dati Organizzazioni da {len(all_dfs_orgs)} fonti...")
            combined_org_df = pd.concat(all_dfs_orgs, ignore_index=True)
            dfs_to_write['Report_Organizzazioni'] = combined_org_df
            
        if all_dfs_repos:
            print(f"\nAggregazione dati Repository da {len(all_dfs_repos)} fonti...")
            combined_repo_df = pd.concat(all_dfs_repos, ignore_index=True)
            dfs_to_write['Report_Repositories'] = combined_repo_df
            
        # Scrive il file Excel
        output_file = get_output_filepath(config["output_dir"]) 
        write_excel_report(dfs_to_write, output_file)

    except Exception as e:
        print(f"\n❌ ERRORE CRITICO DELLO SCRIPT: {e}")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()