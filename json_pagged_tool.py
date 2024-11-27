import json
import os
from openpyxl import Workbook

def load_json(file_path):
    """Wczytuje plik JSON i zwróci jego zawartość."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)


def extract_keys(data, parent_key=''):
    """
    Rekurencyjnie wyodrębnia wszystkie klucze z JSON-a, uwzględniając ich strukturę.
    Zwraca zestaw ścieżek kluczy (np. "key1.key2.key3").
    """
    keys = set()
    for k, v in data.items():
        full_key = f"{parent_key}.{k}" if parent_key else k
        keys.add(full_key)
        if isinstance(v, dict):
            keys.update(extract_keys(v, full_key))
    return keys


def compare_structures(new_json_keys, reference_keys):
    """
    Porównaj strukturę kluczy nowego JSON-a z kluczami referencyjnymi.
    """
    return new_json_keys == reference_keys


def compare_json_files(file1, file2):
    """
    Porównuje dwa pliki JSON i identyfikuje różnice w wartościach pól.

    Args:
        file1 (str): Ścieżka do pierwszego pliku JSON.
        file2 (str): Ścieżka do drugiego pliku JSON.

    Returns:
        tuple: Liczba różnic i lista pól, które się różnią.
    """
    # Wczytaj oba pliki JSON
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            json1 = json.load(f1)
            json2 = json.load(f2)
    except Exception as e:
        print(f"Błąd wczytywania plików: {e}")
        return 0, []

    # Porównaj wartości
    differing_fields = []

    def compare_dicts(d1, d2, parent_key=""):
        """
        Rekurencyjnie porównuje słowniki, uwzględniając zagnieżdżone pola.
        """
        for key in d1:
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(d1[key], dict) and isinstance(d2[key], dict):
                # Rekurencja dla zagnieżdżonych słowników
                compare_dicts(d1[key], d2[key], full_key)
            else:
                # Porównanie wartości
                if d1[key] != d2[key]:
                    differing_fields.append(full_key)

    compare_dicts(json1, json2)

    # Zwróć liczbę różnic i listę różniących się pól
    return len(differing_fields), str(differing_fields)


def main():
    # Tworzenie nowego skoroszytu Excel
    wb = Workbook()
    ws = wb.active

    # Nazwanie arkusza
    ws.title = "Porównanie"

    # Dodanie nagłówków kolumn
    headers = ["Złota wersja", "Wersja testowa", "Ilość błędów", "Błędne klucze"]
    ws.append(headers)

    #foldery z złotymi wersjami jsonami i z testowymi jsonami
    json_check_versions_folder_path = "json_check_versions"
    json_golden_versions_folder_path = "json_golden_versions"

    #pętla iterująca po wszystkich jsonach testowych
    for filename in os.listdir(json_check_versions_folder_path):
        file_path = os.path.join(json_check_versions_folder_path, filename)
        if os.path.isfile(file_path) and filename.endswith('.json'):
            test_json = load_json(file_path)
            test_json_keys = extract_keys(test_json)

            #pętla iterująca po wszystkich złotych wersjach plików json
            golden_version_found = False
            for filename_gold in os.listdir(json_golden_versions_folder_path):
                file_path_gold = os.path.join(json_golden_versions_folder_path, filename_gold)
                if os.path.isfile(file_path_gold) and filename.endswith('.json'):
                    golden_json = load_json(file_path_gold)
                    golden_json_keys = extract_keys(golden_json)

                    #porównywanie struktury plików json (do jakiej złotej wersji pliku json pasuje json testowy)
                    if compare_structures(test_json_keys, golden_json_keys):
                        golden_version_found = True
                        comparison_tuple = compare_json_files(file_path, file_path_gold)
                        name_tuple = (filename_gold, filename)
                        final_tuple = name_tuple + comparison_tuple
                        ws.append(final_tuple)
                        break

            if golden_version_found == False:
                not_found_tuple = ("Brak złotej wersji", filename, "-", )
                ws.append(not_found_tuple)

    nazwa_pliku = "porownanie.xlsx"
    wb.save(nazwa_pliku)
    print(f"Plik {nazwa_pliku} został utworzony.")

if __name__ == '__main__':
    main()