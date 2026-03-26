from __future__ import annotations

import argparse
from collections.abc import Iterable
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
import unicodedata

import pandas as pd
from sqlalchemy import insert, select, tuple_

from app.db.session import SessionLocal
from app.models.shipment import Shipment


CSV_COLUMN_MAPPING = {
    "data do embarque": "data_embarque",
    "origem": "origem",
    "destino": "destino",
    "valor da carga (r$)": "valor_carga",
    "tipo de veiculo": "tipo_veiculo",
    "transportadora": "transportadora",
    "taxa ad valorem (%)": "taxa_ad_valorem_pct",
    "frete peso (r$)": "frete_peso",
    "ocorrencias": "ocorrencia",
    "ad valorem (r$)": "ad_valorem",
}

REQUIRED_COLUMNS = {
    "data_embarque",
    "origem",
    "destino",
    "valor_carga",
    "tipo_veiculo",
    "transportadora",
    "taxa_ad_valorem_pct",
    "frete_peso",
}

REQUIRED_COLUMN_LABELS = {
    "data_embarque": "Data do Embarque",
    "origem": "Origem",
    "destino": "Destino",
    "valor_carga": "Valor da Carga (R$)",
    "tipo_veiculo": "Tipo de Veiculo",
    "transportadora": "Transportadora",
    "taxa_ad_valorem_pct": "Taxa Ad Valorem (%)",
    "frete_peso": "Frete Peso (R$)",
}

DUPLICATE_KEY_COLUMNS = [
    "data_embarque",
    "origem",
    "destino",
    "valor_carga",
    "tipo_veiculo",
    "transportadora",
    "taxa_ad_valorem_pct",
    "frete_peso",
    "ocorrencia",
]

DECIMAL_2 = Decimal("0.01")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Importa um CSV logistico para a tabela shipments.",
    )
    parser.add_argument("csv_path", type=Path, help="Caminho para o arquivo CSV.")
    return parser.parse_args()


def normalize_text(value: object) -> str:
    if value is None or pd.isna(value):
        return ""
    return " ".join(str(value).strip().split())


def normalize_header(value: object) -> str:
    normalized = normalize_text(value).casefold()
    return (
        unicodedata.normalize("NFKD", normalized)
        .encode("ascii", "ignore")
        .decode("ascii")
    )


def normalize_occurrence(value: object) -> str:
    normalized = normalize_text(value)
    if not normalized:
        return "OK"
    if normalized.upper() == "OK":
        return "OK"
    return normalized


def require_text(value: object, field_name: str) -> str:
    normalized = normalize_text(value)
    if not normalized:
        raise ValueError(f"Campo obrigatorio '{field_name}' vazio.")
    return normalized


def normalize_decimal_string(value: str) -> str:
    cleaned = value.strip()
    cleaned = cleaned.replace("R$", "").replace("%", "").replace(" ", "")

    if not cleaned:
        raise ValueError("Valor decimal ausente.")

    sign = ""
    if cleaned[0] in {"+", "-"}:
        sign = cleaned[0]
        cleaned = cleaned[1:]

    if not cleaned:
        raise ValueError("Valor decimal invalido.")

    comma_count = cleaned.count(",")
    dot_count = cleaned.count(".")

    if comma_count and dot_count:
        decimal_separator = "," if cleaned.rfind(",") > cleaned.rfind(".") else "."
        thousands_separator = "." if decimal_separator == "," else ","
        cleaned = cleaned.replace(thousands_separator, "")
        if decimal_separator == ",":
            cleaned = cleaned.replace(",", ".")
    elif comma_count > 1:
        parts = cleaned.split(",")
        if all(part.isdigit() for part in parts) and all(len(part) == 3 for part in parts[1:]):
            cleaned = "".join(parts)
        else:
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
    elif dot_count > 1:
        parts = cleaned.split(".")
        if all(part.isdigit() for part in parts) and all(len(part) == 3 for part in parts[1:]):
            cleaned = "".join(parts)
        else:
            cleaned = "".join(parts[:-1]) + "." + parts[-1]
    elif comma_count == 1 and dot_count == 0:
        integer_part, decimal_part = cleaned.split(",")
        if integer_part.isdigit() and decimal_part.isdigit() and len(decimal_part) == 3 and len(integer_part) <= 3:
            cleaned = integer_part + decimal_part
        else:
            cleaned = integer_part + "." + decimal_part
    elif dot_count == 1 and comma_count == 0:
        integer_part, decimal_part = cleaned.split(".")
        if integer_part.isdigit() and decimal_part.isdigit() and len(decimal_part) == 3 and len(integer_part) <= 3:
            cleaned = integer_part + decimal_part

    return sign + cleaned


def parse_decimal(value: object) -> Decimal:
    if value is None or pd.isna(value):
        raise ValueError("Valor decimal ausente.")

    if isinstance(value, Decimal):
        decimal_value = value
    elif isinstance(value, (int, float)):
        decimal_value = Decimal(str(value))
    else:
        try:
            decimal_value = Decimal(normalize_decimal_string(str(value)))
        except InvalidOperation as exc:
            raise ValueError(f"Valor decimal invalido: {value!r}") from exc

    return decimal_value.quantize(DECIMAL_2, rounding=ROUND_HALF_UP)


def parse_date(value: object) -> date:
    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Data invalida: {value!r}")
    return parsed.date()


def load_csv(csv_path: Path) -> pd.DataFrame:
    if not csv_path.exists():
        raise FileNotFoundError(f"Arquivo nao encontrado: {csv_path}")

    last_error: Exception | None = None
    for encoding in ("utf-8-sig", "latin-1"):
        try:
            return pd.read_csv(csv_path, sep=None, engine="python", encoding=encoding)
        except Exception as exc:
            last_error = exc

    raise RuntimeError(f"Nao foi possivel ler o CSV: {csv_path}") from last_error


def rename_columns(dataframe: pd.DataFrame) -> pd.DataFrame:
    dataframe = dataframe.rename(columns=lambda column: str(column).strip())
    dataframe = dataframe.rename(
        columns={
            column: CSV_COLUMN_MAPPING[normalize_header(column)]
            for column in dataframe.columns
            if normalize_header(column) in CSV_COLUMN_MAPPING
        }
    )

    if "ocorrencia" not in dataframe.columns:
        dataframe["ocorrencia"] = ""

    missing_columns = REQUIRED_COLUMNS - set(dataframe.columns)
    if missing_columns:
        missing = ", ".join(REQUIRED_COLUMN_LABELS[column] for column in sorted(missing_columns))
        raise ValueError(f"Colunas obrigatorias ausentes no CSV: {missing}")

    allowed_columns = REQUIRED_COLUMNS | {"ocorrencia", "ad_valorem"}
    return dataframe[[column for column in dataframe.columns if column in allowed_columns]]


def build_records(dataframe: pd.DataFrame) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []

    for row_number, row in enumerate(dataframe.to_dict(orient="records"), start=2):
        try:
            ocorrencia = normalize_occurrence(row.get("ocorrencia"))
            valor_carga = parse_decimal(row.get("valor_carga"))
            taxa_ad_valorem_pct = parse_decimal(row.get("taxa_ad_valorem_pct"))

            ad_valorem_raw = row.get("ad_valorem")
            if ad_valorem_raw is None or pd.isna(ad_valorem_raw) or normalize_text(ad_valorem_raw) == "":
                ad_valorem = (valor_carga * taxa_ad_valorem_pct / Decimal("100")).quantize(
                    DECIMAL_2,
                    rounding=ROUND_HALF_UP,
                )
            else:
                ad_valorem = parse_decimal(ad_valorem_raw)

            record = {
                "data_embarque": parse_date(row.get("data_embarque")),
                "origem": require_text(row.get("origem"), "origem"),
                "destino": require_text(row.get("destino"), "destino"),
                "valor_carga": valor_carga,
                "tipo_veiculo": require_text(row.get("tipo_veiculo"), "tipo_veiculo"),
                "transportadora": require_text(row.get("transportadora"), "transportadora"),
                "taxa_ad_valorem_pct": taxa_ad_valorem_pct,
                "frete_peso": parse_decimal(row.get("frete_peso")),
                "ocorrencia": ocorrencia,
                "tem_ocorrencia": ocorrencia != "OK",
                "ad_valorem": ad_valorem,
            }
        except ValueError as exc:
            raise ValueError(f"Erro na linha {row_number}: {exc}") from exc

        records.append(record)

    return records


def unique_records(records: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    unique_items: list[dict[str, object]] = []
    seen_keys: set[tuple[object, ...]] = set()

    for record in records:
        key = tuple(record[column] for column in DUPLICATE_KEY_COLUMNS)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        unique_items.append(record)

    return unique_items


def filter_existing_records(records: list[dict[str, object]]) -> list[dict[str, object]]:
    if not records:
        return []

    candidate_keys = [tuple(record[column] for column in DUPLICATE_KEY_COLUMNS) for record in records]

    with SessionLocal() as session:
        existing_keys = set(
            session.execute(
                select(
                    Shipment.data_embarque,
                    Shipment.origem,
                    Shipment.destino,
                    Shipment.valor_carga,
                    Shipment.tipo_veiculo,
                    Shipment.transportadora,
                    Shipment.taxa_ad_valorem_pct,
                    Shipment.frete_peso,
                    Shipment.ocorrencia,
                ).where(
                    tuple_(
                        Shipment.data_embarque,
                        Shipment.origem,
                        Shipment.destino,
                        Shipment.valor_carga,
                        Shipment.tipo_veiculo,
                        Shipment.transportadora,
                        Shipment.taxa_ad_valorem_pct,
                        Shipment.frete_peso,
                        Shipment.ocorrencia,
                    ).in_(candidate_keys)
                )
            ).tuples()
        )

    return [
        record
        for record in records
        if tuple(record[column] for column in DUPLICATE_KEY_COLUMNS) not in existing_keys
    ]


def insert_records(records: list[dict[str, object]]) -> int:
    if not records:
        return 0

    with SessionLocal() as session:
        session.execute(insert(Shipment), records)
        session.commit()

    return len(records)


def main() -> None:
    try:
        args = parse_args()

        dataframe = load_csv(args.csv_path)
        dataframe = rename_columns(dataframe)
        records = build_records(dataframe)

        total_rows = len(records)
        unique_input_records = unique_records(records)
        skipped_inside_file = total_rows - len(unique_input_records)
        records_to_insert = filter_existing_records(unique_input_records)
        skipped_existing = len(unique_input_records) - len(records_to_insert)
        inserted = insert_records(records_to_insert)

        print(f"Linhas lidas: {total_rows}")
        print(f"Duplicadas no arquivo ignoradas: {skipped_inside_file}")
        print(f"Ja existentes no banco ignoradas: {skipped_existing}")
        print(f"Registros inseridos: {inserted}")
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        raise SystemExit(f"Erro no import: {exc}") from exc
    except Exception as exc:
        raise SystemExit(f"Erro inesperado no import: {exc}") from exc


if __name__ == "__main__":
    main()
