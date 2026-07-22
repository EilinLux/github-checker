import pandas as pd
import sys
import os

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
    - set_org_owners (Lista A)
    - set_repo_collaborators (Lista B)
    """
    print(f"Caricamento file principale: {filename}...")
    try:
        # Leggi Foglio 1: Lista A (Proprietari Org)
        df_orgs = pd.read_excel(filename, sheet_name='Report_Organizzazioni')
        if 'Role' not in df_orgs.columns or 'User' not in df_orgs.columns:
            print("ERRORE: Il foglio 'Report_Organizzazioni' non contiene le colonne 'User' e 'Role'.")
            return None, None
            
        org_owners = df_orgs[df_orgs['Role'].str.lower() == 'admin']['User']
        set_org_owners = set(org_owners)
        print(f"Trovati {len(set_org_owners)} Proprietari di Organizzazione (Lista A).")

        # Leggi Foglio 2: Lista B (Collaboratori Diretti)
        df_repos = pd.read_excel(filename, sheet_name='Report_Repositories')
        col_name = 'Permessi Scrittura (Collaboratori Diretti)'
        if col_name not in df_repos.columns:
            print(f"ERRORE: Il foglio 'Report_Repositories' non contiene la colonna '{col_name}'.")
            return None, None
        
        # Filtra i placeholder
        placeholders = ['Nessun Collaboratore Diretto', 'N/A']
        repo_collaborators = df_repos[~df_repos[col_name].isin(placeholders)][col_name]
        set_repo_collaborators = set(repo_collaborators)
        print(f"Trovati {len(set_repo_collaborators)} Collaboratori Diretti unici (Lista B).")
        
        return set_org_owners, set_repo_collaborators

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
    - set_team_members (Lista C)
    """
    print(f"Caricamento file Team: {filename}...")
    try:
        # Leggi Foglio 3: Lista C (Membri Team)
        df_teams = pd.read_excel(filename, sheet_name='Report_Teams')
        if 'User' not in df_teams.columns:
            print("ERRORE: Il foglio 'Report_Teams' non contiene la colonna 'User'.")
            return None
            
        # Filtra i placeholder
        team_members = df_teams[df_teams['User'] != 'Nessun membro']['User']
        set_team_members = set(team_members)
        print(f"Trovati {len(set_team_members)} Utenti unici con accesso via Team (Lista C).")
        
        return set_team_members

    except (FileNotFoundError, KeyError, ValueError) as e:
        print(f"ERRORE durante il caricamento del file Team: {e}")
        print("Assicurati che il nome del file e il nome del foglio ('Report_Teams') siano corretti.")
        return None
    except Exception as e:
        print(f"ERRORE imprevisto: {e}")
        return None

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
    
    # --- 2. Carica i dati ---
    org_owners, repo_collaborators = load_main_report_data(main_report_file)
    if org_owners is None:
        sys.exit(1)
        
    team_members = load_team_report_data(team_report_file)
    if team_members is None:
        sys.exit(1)
        
    # --- 3. Esegui il confronto ---
    
    # Uniamo Lista B (Collaboratori) e Lista C (Membri Team)
    # Questa è la lista di tutti gli utenti con accesso *esplicito*
    all_explicit_access = repo_collaborators.union(team_members)
    
    # *** Confronto 1: Proprietari con Accesso Implicito (A - (B U C)) ***
    implicit_admins = org_owners.difference(all_explicit_access)
    
    # *** Confronto 2: Accesso Esplicito (Non-Proprietari) ((B U C) - A) ***
    explicit_non_owners = all_explicit_access.difference(org_owners)
    
    # --- 4. Stampa i risultati ---
    print("\n--- Riepilogo Dati ---")
    
    print(f"Lista A (Proprietari Org): {len(org_owners)} utenti")
    # print(f"Dettaglio: {sorted(list(org_owners))}") # Decommenta per debug
    
    print(f"Lista B+C (Accesso Esplicito via Repo o Team): {len(all_explicit_access)} utenti")
    # print(f"Dettaglio: {sorted(list(all_explicit_access))}") # Decommenta per debug
    
    print("\n--- \u2193\ufe0f Report Finale \u2193\ufe0f ---")

    # --- Stampa Elenco 1 (NUOVO) ---
    print("\n--- 1. Elenco Completo Proprietari (Tutta la Lista A) ---")
    if not org_owners:
        print("Info: Nessun Proprietario di Organizzazione (admin) è stato trovato.")
    else:
        print(f"ℹ️ Info: Trovati {len(org_owners)} Proprietari (admin) totali per le organizzazioni analizzate:\n")
        count = 1
        for user in sorted(list(org_owners)):
            print(f"     {count}. {user}")
            count += 1
    
    # --- Stampa Confronto 2 (ex-1) ---
    print("\n--- 2. Proprietari con Accesso Implicito (A - (B U C)) ---")
    if not implicit_admins:
        print("✅ Buone notizie: Nessun 'Proprietario con Accesso Implicito' trovato.")
        print("   Tutti i Proprietari dell'Organizzazione hanno anche un accesso esplicito")
        print("   (o come collaboratori diretti o tramite un team) ai repository.")
    else:
        print(f"🔥 ATTENZIONE: Trovati {len(implicit_admins)} Proprietari con Accesso Implicito:")
        print("   Questi utenti hanno privilegi di AMMINISTRATORE su TUTTI i repository,")
        print("   anche se non sono elencati come collaboratori o membri di team specifici.\n")
        count = 1
        for user in sorted(list(implicit_admins)):
            print(f"     {count}. {user}")
            count += 1

    # --- Stampa Confronto 3 (ex-2) ---
    print("\n--- 3. Accesso Esplicito (Non-Proprietari) ((B U C) - A) ---")
    if not explicit_non_owners:
        print("✅ Info: Nessun utente con accesso esplicito trovato al di fuori dei Proprietari.")
        print("   Tutti gli accessi ai repository sono gestiti da utenti che sono anche Proprietari.")
    else:
        print(f"ℹ️ Info: Trovati {len(explicit_non_owners)} utenti con Accesso Esplicito che NON sono Proprietari:")
        print("   Questi utenti hanno accesso (come collaboratori o via team)")
        print("   ma non hanno privilegi di amministratore a livello di organizzazione.\n")
        count = 1
        for user in sorted(list(explicit_non_owners)):
            print(f"     {count}. {user}")
            count += 1

if __name__ == "__main__":
    main()