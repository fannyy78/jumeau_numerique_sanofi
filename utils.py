import csv
import pandas as pd

def detect_delimiter(fichier):
    with open(fichier, 'r', newline='', encoding='utf-8', errors='replace') as f:
        sample = f.read(4096)  # plus grand échantillon
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample)
            return dialect.delimiter
        except csv.Error:
            # Fallback intelligent basé sur la fréquence
            if ';' in sample and sample.count(';') > sample.count(','):
                return ';'
            elif '\t' in sample:
                return '\t'
            else:
                return ','

def detect_header(fichier, sep=None):
    """
    Détecte la ligne d'en-tête dans un fichier CSV ou Excel.
    """
    if fichier.lower().endswith('.csv'):
        if sep is None:
            sep = detect_delimiter(fichier)

        with open(fichier, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                # ignore lignes vides
                if not line.strip():
                    continue
                # on split proprement en respectant les guillemets
                reader = csv.reader([line], delimiter=sep, quotechar='"')
                cols = next(reader)
                if len(cols) > 1:
                    return i
        return 0

    elif fichier.lower().endswith(('.xlsx', '.xls')):
        try:
            df = pd.read_excel(
                fichier, header=None, nrows=5,
                engine='openpyxl' if fichier.lower().endswith('.xlsx') else 'xlrd'
            )
            for i, row in df.iterrows():
                if row.notna().sum() > 1:
                    return i
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier Excel: {e}")

    return 0
def detect_header(fichier, sep=None):
    """
    Détecte la ligne d'en-tête dans un fichier CSV ou Excel (.xls, .xlsx, .xlsm).
    """
    if fichier.lower().endswith('.csv'):
        if sep is None:
            sep = detect_delimiter(fichier)

        with open(fichier, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if not line.strip():
                    continue
                reader = csv.reader([line], delimiter=sep, quotechar='"')
                cols = next(reader)
                if len(cols) > 1:
                    return i
        return 0

    elif fichier.lower().endswith(('.xlsx', '.xls', '.xlsm')):
        try:
            engine = 'openpyxl' if fichier.lower().endswith(('.xlsx', '.xlsm')) else 'xlrd'
            df = pd.read_excel(fichier, header=None, nrows=5, engine=engine)
            for i, row in df.iterrows():
                if row.notna().sum() > 1:
                    return i
        except Exception as e:
            print(f"Erreur lors de la lecture du fichier Excel: {e}")

    return 0
