import pandas as pd
import sys
import os
import traceback
from datetime import datetime

# --- Costante per la cartella di output ---
OUTPUT_DIR = "output"

def prompt_for_file(prompt_message):
    """
    Chiede all'utente un nome di file finché non ne inserisce uno valido ed esistente.
    """
    while True:
        filename = input(prompt_message).strip()
        if not os.path.exists(filename):
            print(f"ERRORE: File non trovato: '{filename}'")
            print("Assicurati che il file sia nella stessa cartella dello script o inserisci il percorso completo.")
        else:
            return filename

def load_main_report_data(filename):
    """
    Carica i dati dai fogli 'Report_Organizzazioni' e 'Report_Repositories'.
    
    Restituisce:
    - org_owners_df (Lista A come DataFrame)
    - df_repo_collabs (Lista B come DataFrame)
    """
    print(f"Caricamento file principale: {filename}...")
    try:
        # Leggi Foglio 1: Lista A (Proprietari Org)
        df_orgs = pd.read_excel(filename, sheet_name='Report_Organizzazioni')
        if 'Role' not in df_orgs.columns or 'User' not in df_orgs.columns or 'Organizzazione' not in df_orgs.columns:
            print("ERRORE: Il foglio 'Report_Organizzazioni' non contiene le colonne 'User', 'Role' e 'Organizzazione'.")
            return None, None
            
        org_owners_df = df_orgs[df_orgs['Role'].str.lower() == 'admin'][['User', 'Organizzazione']].drop_duplicates().reset_index(drop=True)
        print(f"Trovate {len(org_owners_df)} righe Proprietario/Organizzazione (Lista A).")

        # Leggi Foglio 2: Lista B (Collaboratori Diretti)
        df_repos = pd.read_excel(filename, sheet_name='Report_Repositories')
        col_name = 'Permessi Scrittura (Collaboratori Diretti)'
        if col_name not in df_repos.columns or 'Nome Repo' not in df_repos.columns:
            print(f"ERRORE: Il foglio 'Report_Repositories' non contiene le colonne '{col_name}' e 'Nome Repo'.")
            return None, None
        
        # Filtra i placeholder
        placeholders = ['Nessun Collaboratore Diretto', 'N/A']
        df_repo_collabs = df_repos[~df_repos[col_name].isin(placeholders)][[col_name, 'Nome Repo']]
        df_repo_collabs.columns = ['User', 'Repository'] # Rinomina per coerenza
        
        # Estrai l'organizzazione dal nome del repo (es. "mia-org/mio-repo")
        df_repo_collabs['Organizzazione'] = df_repo_collabs['Repository'].apply(lambda x: x.split('/')[0])
        
        print(f"Trovate {len(df_repo_collabs)} righe Collaboratore Diretto/Repo (Lista B).")
        
        return org_owners_df, df_repo_collabs

    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"ERRORE durante il caricamento del file principale: {e}")
        print("Assicurati che il nome del file e i nomi dei fogli ('Report_Organizzazioni', 'Report_Repositories') siano corretti.")
        return None, None
    except Exception as e:
        print(f"ERRORE imprevisto: {e}")
        return None, None

def load_team_report_data(filename):
    """
    Carica i dati dal foglio 'Report_Teams'.
    
    Restituisce:
    - df_team_members (Lista C come DataFrame)
    """
    print(f"Caricamento file Team: {filename}...")
    try:
        # Leggi Foglio 3: Lista C (Membri Team)
        df_teams = pd.read_excel(filename, sheet_name='Report_Teams')
        if 'User' not in df_teams.columns or 'Organizzazione' not in df_teams.columns or 'Team Name' not in df_teams.columns:
            print("ERRORE: Il foglio 'Report_Teams' non contiene le colonne 'User', 'Organizzazione' e 'Team Name'.")
            return None
            
        # Filtra i placeholder
        df_team_members = df_teams[df_teams['User'] != 'Nessun membro'][['User', 'Organizzazione', 'Team Name']].drop_duplicates().reset_index(drop=True)
        print(f"Trovate {len(df_team_members)} righe Utente/Team/Organizzazione (Lista C).")
        
        return df_team_members

    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"ERRORE durante il caricamento del file Team: {e}")
        print("Assicurati che il nome del file e il nome del foglio ('Report_Teams') siano corretti.")
        return None
    except Exception as e:
        print(f"ERRORE imprevisto: {e}")
        return None

# --- NUOVE FUNZIONI PER SCRIVERE L'EXCEL DI ANALISI ---

def get_output_filepath_for_analysis():
    """
    Crea un percorso di file univoco per il report di analisi.
    """
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"github_permissions_ANALYSIS_{timestamp}.xlsx"
    return os.path.join(OUTPUT_DIR, filename)

def write_analysis_report(output_file, df_all_owners, df_implicit_admins, df_explicit_non_owners):
    """
    Scrive i 3 DataFrame di risultati in 3 fogli di un file Excel.
    """
    print(f"\nSalvataggio del report di analisi su file: {output_file}")
    
    try:
        # --- LOGICA CORRETTA ---
        # 1. Crea un dizionario che mappa i nomi dei fogli ai DataFrame
        dfs_to_write = {
            '1_Proprietari_Totali': df_all_owners,
            '2_Accesso_Implicito_Admin': df_implicit_admins,
            '3_Accesso_Esplicito_Non_Admin': df_explicit_non_owners
        }

        with pd.ExcelWriter(output_file, engine='xlsxwriter') as writer:
            
            # 2. Itera sul dizionario
            for sheet_name, df in dfs_to_write.items():
                
                # Salta i fogli vuoti
                if df.empty:
                    print(f"Info: Foglio '{sheet_name}' è vuoto, lo salto.")
                    continue
                    
                print(f"Scrittura foglio: {sheet_name} ({len(df)} righe)")
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # 3. Ora abbiamo accesso sia a 'df' (per i dati) che a 'worksheet'
                worksheet = writer.sheets[sheet_name]
                
                # Itera sulle colonne del DataFrame 'df'
                for idx, col in enumerate(df.columns):
                    series = df[col]
                    max_len = max((series.astype(str).map(len).max() or 0), len(col)) + 2
                    worksheet.set_column(idx, idx, min(max_len, 75))
            
        print("Report di analisi salvato con successo.")
        # --- FINE DELLA CORREZIONE ---

    except Exception as e:
        print(f"ERRORE: Impossibile scrivere il file Excel di analisi. {e}")
        print(traceback.format_exc())

# ---------------------------------------------------

def main():
    """
    Funzione principale per orchestrare il confronto.
    """
    print("--- Analizzatore di Permessi Impliciti GitHub ---")
    print("Questo script confronta 3 liste per trovare i Proprietari (Owner) che hanno accesso")
    print("ai repository *solo* grazie al loro ruolo a livello di Organizzazione.\n")
    
    # --- 1. Ottieni i nomi dei file ---
    main_report_file = prompt_for_file("Inserisci il nome del file Excel del report PRINCIPALE (Org + Repo): ")
    team_report_file = prompt_for_file("Inserisci il nome del file Excel del report TEAM: ")
    
    print("\n--- Inizio Elaborazione ---")
    
    # --- 2. Carica i dati (ora sono DataFrame) ---
    org_owners_df, df_repo_collabs = load_main_report_data(main_report_file)
    if org_owners_df is None:
        sys.exit(1)
        
    df_team_members = load_team_report_data(team_report_file)
    if df_team_members is None:
        sys.exit(1)
        
    # --- 3. Esegui il confronto (usando la logica dei DataFrame) ---
    
    # Lista A (Proprietari) è 'org_owners_df'
    
    # Creiamo Lista B+C (Accesso Esplicito)
    explicit_repo_df = df_repo_collabs[['User', 'Organizzazione', 'Repository']]
    explicit_repo_df = explicit_repo_df.rename(columns={'Repository': 'Dettaglio'})
    explicit_repo_df['Tipo Accesso'] = 'Collaboratore Diretto'
    
    explicit_team_df = df_team_members[['User', 'Organizzazione', 'Team Name']]
    explicit_team_df = explicit_team_df.rename(columns={'Team Name': 'Dettaglio'})
    explicit_team_df['Tipo Accesso'] = 'Membro Team'
    
    # 'all_explicit_access_df' contiene tutti gli accessi espliciti
    all_explicit_access_df = pd.concat([explicit_repo_df, explicit_team_df]).drop_duplicates()
    
    # Per il confronto, abbiamo solo bisogno della combinazione unica Utente/Organizzazione
    all_explicit_users_orgs_df = all_explicit_access_df[['User', 'Organizzazione']].drop_duplicates()
    
    
    # *** Confronto 1: Proprietari con Accesso Implicito (A - (B U C)) ***
    # Troviamo le righe in A che non hanno corrispondenza in (B U C)
    # per la stessa coppia (User, Organizzazione)
    implicit_admins_df = pd.merge(
        org_owners_df, 
        all_explicit_users_orgs_df, 
        on=['User', 'Organizzazione'], 
        how='left', 
        indicator=True
    )
    implicit_admins_df = implicit_admins_df[implicit_admins_df['_merge'] == 'left_only'][['User', 'Organizzazione']]
    
    
    # *** Confronto 2: Accesso Esplicito (Non-Proprietari) ((B U C) - A) ***
    # Troviamo le righe in (B U C) che non hanno corrispondenza in A
    # per la stessa coppia (User, Organizzazione)
    explicit_non_owners_df = pd.merge(
        all_explicit_access_df, 
        org_owners_df, 
        on=['User', 'Organizzazione'], 
        how='left', 
        indicator=True
    )
    explicit_non_owners_df = explicit_non_owners_df[explicit_non_owners_df['_merge'] == 'left_only'][['User', 'Organizzazione', 'Tipo Accesso', 'Dettaglio']]
    
    
    # --- 4. Stampa i risultati (Console) ---
    print("\n--- Riepilogo Dati ---")
    
    print(f"Lista A (Proprietari Org): {len(org_owners_df)} righe (User/Org)")
    print(f"Lista B+C (Accesso Esplicito): {len(all_explicit_access_df)} righe (User/Org/Accesso)")
    
    print("\n--- \u2193\ufe0f Report Finale (Console) \u2193\ufe0f ---")

    # --- Stampa Elenco 1 ---
    print("\n--- 1. Elenco Completo Proprietari (Tutta la Lista A) ---")
    if org_owners_df.empty:
        print("Info: Nessun Proprietario di Organizzazione (admin) è stato trovato.")
    else:
        print(f"ℹ️ Info: Trovati {len(org_owners_df)} record Proprietario/Organizzazione:")
        print(org_owners_df.to_string(index=False))
    
    # --- Stampa Confronto 2 ---
    print("\n--- 2. Proprietari con Accesso Implicito (A - (B U C)) ---")
    if implicit_admins_df.empty:
        print("✅ Buone notizie: Nessun 'Proprietario con Accesso Implicito' trovato.")
        print("   Tutti i Proprietari hanno anche un accesso esplicito in ogni organizzazione che amministrano.")
    else:
        print(f"🔥 ATTENZIONE: Trovate {len(implicit_admins_df)} righe di 'Proprietari con Accesso Implicito':")
        print("   Questi utenti amministrano l'organizzazione ma non hanno accessi espliciti (via team/repo).")
        print(implicit_admins_df.to_string(index=False))

    # --- Stampa Confronto 3 ---
    print("\n--- 3. Accesso Esplicito (Non-Proprietari) ((B U C) - A) ---")
    if explicit_non_owners_df.empty:
        print("✅ Info: Nessun utente con accesso esplicito trovato al di fuori dei Proprietari.")
    else:
        print(f"ℹ️ Info: Trovate {len(explicit_non_owners_df)} righe di 'Accesso Esplicito (Non-Proprietari)':")
        print("   Questi utenti hanno accesso a team/repo senza essere amministratori dell'org.")
        print(explicit_non_owners_df.to_string(index=False))
            
    # --- 5. Salva Report su Excel ---
    try:
        output_file = get_output_filepath_for_analysis()
        write_analysis_report(output_file, org_owners_df, implicit_admins_df, explicit_non_owners_df)
    except Exception as e:
        print(f"\nERRORE during il salvataggio del report Excel: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    main()