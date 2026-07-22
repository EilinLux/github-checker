import os
import sys
import time
import jwt # Richiede 'pip install PyJWT'
import requests
import yaml # Importato per l'output YAML
from dotenv import load_dotenv
from datetime import datetime, timezone

def load_env_vars():
    """Carica le variabili .env necessarie per questo script."""
    load_dotenv()
    app_id = os.getenv("GITHUB_APP_ID")
    key_path = os.getenv("GITHUB_PRIVATE_KEY_PATH")

    if not app_id or not key_path:
        print("Errore: GITHUB_APP_ID e GITHUB_PRIVATE_KEY_PATH devono essere impostati nel file .env.", file=sys.stderr)
        sys.exit(1)
        
    try:
        with open(key_path, 'r') as f:
            private_key = f.read()
    except FileNotFoundError:
        print(f"Errore: File della chiave privata non trovato in '{key_path}'", file=sys.stderr)
        sys.exit(1)
        
    return app_id, private_key

def generate_app_jwt(app_id, private_key):
    """Genera il JWT della GitHub App."""
    try:
        now = int(time.time())
        payload = {
            'iat': now - 60,         # Issued at time (60 secondi fa per clock skew)
            'exp': now + (10 * 60),  # Expiration time (10 minuti da ora)
            'iss': app_id            # Issuer (App ID)
        }
        
        # Firma il token con la chiave privata
        token = jwt.encode(
            payload,
            private_key,
            algorithm='RS256'
        )
        return token
        
    except Exception as e:
        print(f"Errore durante la generazione del JWT: {e}", file=sys.stderr)
        return None

def list_github_app_installations(app_id, private_key):
    """
    Recupera TUTTE le installazioni della GitHub App, gestendo la paginazione.
    """
    _jwt = generate_app_jwt(app_id, private_key)
    if not _jwt:
        return None

    headers = {
        'Authorization': f'Bearer {_jwt}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    # Inizia con la prima pagina, 100 risultati per pagina (massimo)
    url = 'https://api.github.com/app/installations?per_page=100'
    all_installations = []

    print("Recupero installazioni (pagina 1)...")

    while url:
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            # Aggiungi i risultati di questa pagina alla lista totale
            data = response.json()
            if isinstance(data, list):
                all_installations.extend(data)
                print(f"Trovate {len(data)} installazioni. Totale finora: {len(all_installations)}")
            else:
                # Caso strano in cui la risposta non è una lista
                print(f"Risposta API inattesa: {data}", file=sys.stderr)
                all_installations.append(data)


            # --- Gestione Paginazione ---
            # Controlla l'header 'Link' per la pagina successiva
            if 'link' in response.headers:
                links = response.headers['link'].split(', ')
                next_url = None
                for link in links:
                    if 'rel="next"' in link:
                        # Estrai l'URL dal link (es. <url>; rel="next")
                        next_url = link.split(';')[0].strip('<>')
                        break
                
                if next_url:
                    print("Recupero pagina successiva...")
                    url = next_url
                else:
                    url = None # Fine del loop, non c'è 'next'
            else:
                url = None # Fine del loop, non c'è header 'link'

        except requests.exceptions.RequestException as e:
            print(f"Errore during il recupero delle installazioni: {e}", file=sys.stderr)
            if e.response is not None:
                print(f"Risposta: {e.response.text}", file=sys.stderr)
            return None # Interrompi in caso di errore
            
    return all_installations

def main():
    """Esecuzione principale per trovare e salvare le installazioni."""
    print("Ricerca delle installazioni della GitHub App...")
    app_id, private_key = load_env_vars()
    
    installations = list_github_app_installations(app_id, private_key)

    if not installations:
        print("Nessuna installazione trovata per questa GitHub App.")
        print("Assicurati di aver installato l'app su almeno un'organizzazione o un account utente.")
        return

    output_list = []
    
    print("\n--- Installazioni Trovate ---")
    print("Trova l'account (organizzazione o utente) che desideri analizzare e")
    print("copia il suo 'ID' nel campo GITHUB_INSTALLATION_ID nel tuo file .env.\n")
    
    for install in installations:
        account_login = install['account']['login']
        account_type = install['account']['type']
        installation_id = install['id']
        
        # Prepara i dati per l'output
        install_data = {
            'account_login': account_login,
            'account_type': account_type,
            'installation_id': installation_id,
            'target_type': install['target_type'],
            'repositories_url': install['repositories_url']
        }
        output_list.append(install_data)

        # Stampa sul terminale per un feedback immediato
        print("===============================================")
        print(f"   Account Login: {account_login} ({account_type})")
        print(f"   ID: {installation_id}   <-- QUESTO È L'INSTALLATION_ID")
        print(f"   Target Type: {install['target_type']}")
        print("===============================================")

    # Prepara i dati finali per il YAML
    output_yaml_data = {'installations': output_list}
    output_filename = 'installations.yaml'

    # Salva i dati in un file YAML
    try:
        with open(output_filename, 'w') as f:
            yaml.dump(output_yaml_data, f, sort_keys=False, default_flow_style=False)
        print(f"\n✅ Dettagli completi salvati con successo in: {output_filename}")
    except Exception as e:
        print(f"\n❌ Errore during il salvataggio del file YAML: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()