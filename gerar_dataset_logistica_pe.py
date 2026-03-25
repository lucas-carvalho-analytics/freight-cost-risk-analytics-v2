import csv
import random
from datetime import datetime, timedelta

SEED = 42
N = 5000
ARQUIVO_SAIDA = "dataset_operacoes_logisticas_pe.csv"

random.seed(SEED)

ORIGENS = ["Suape", "Jaboatão"]

DESTINOS = {
    "Fábrica Recife/PE": 45,
    "Fábrica Goiana/PE": 85,
    "Fábrica Vitória de Santo Antão/PE": 60,
    "Fábrica Caruaru/PE": 135,
    "Fábrica Garanhuns/PE": 235,
    "Fábrica Petrolina/PE": 720,
    "Fábrica João Pessoa/PB": 125,
    "Fábrica Campina Grande/PB": 190,
    "Fábrica Patos/PB": 405,
    "Fábrica Cajazeiras/PB": 505,
}
PESOS_DESTINOS = [0.12, 0.15, 0.12, 0.14, 0.08, 0.04, 0.12, 0.12, 0.07, 0.04]

TRANSPORTADORAS = ["Belmont-Alpha", "Trans-X"]

VEICULOS = {
    "VUC": {"peso_min_t": 2, "peso_max_t": 6, "fator_frete": 0.78, "valor_mult": 0.90},
    "Toco": {"peso_min_t": 4, "peso_max_t": 10, "fator_frete": 0.66, "valor_mult": 0.95},
    "Truck": {"peso_min_t": 8, "peso_max_t": 16, "fator_frete": 0.54, "valor_mult": 1.00},
    "Carreta": {"peso_min_t": 18, "peso_max_t": 28, "fator_frete": 0.46, "valor_mult": 1.08},
    "Bitrem": {"peso_min_t": 25, "peso_max_t": 38, "fator_frete": 0.40, "valor_mult": 1.12},
}
PESOS_VEICULOS = [0.10, 0.15, 0.30, 0.30, 0.15]

DATA_INICIO = datetime(2024, 1, 1)
DATA_FIM = datetime(2025, 12, 31)


def data_aleatoria(inicio, fim):
    delta = fim - inicio
    return inicio + timedelta(days=random.randint(0, delta.days))


def gerar_peso_toneladas(tipo_veiculo):
    cfg = VEICULOS[tipo_veiculo]
    return round(random.uniform(cfg["peso_min_t"], cfg["peso_max_t"]), 2)


def gerar_valor_carga(tipo_veiculo, peso_t):
    base = random.triangular(50_000, 500_000, 180_000)
    ajuste_peso = peso_t * random.uniform(800, 2_200)
    valor = (base + ajuste_peso) * VEICULOS[tipo_veiculo]["valor_mult"]
    return round(min(max(valor, 50_000), 500_000), 2)


def gerar_taxa_ad_valorem(valor_carga, distancia_km):
    taxa = random.uniform(0.07, 0.15)
    if valor_carga > 350_000:
        taxa += random.uniform(0.008, 0.018)
    if distancia_km > 300:
        taxa += random.uniform(0.003, 0.012)
    return round(min(taxa, 0.18), 4)


def gerar_ocorrencia(distancia_km):
    if distancia_km <= 100:
        p_sinistro, p_atraso = 0.01, 0.07
    elif distancia_km <= 250:
        p_sinistro, p_atraso = 0.015, 0.11
    else:
        p_sinistro, p_atraso = 0.025, 0.18

    r = random.random()
    if r < p_sinistro:
        return "Sinistro"
    if r < p_sinistro + p_atraso:
        return "Atraso"
    return "OK"


def gerar_frete_peso(tipo_veiculo, distancia_km, ocorrencia):
    peso_t = gerar_peso_toneladas(tipo_veiculo)
    fator = VEICULOS[tipo_veiculo]["fator_frete"]

    frete = 250 + (peso_t * distancia_km * fator)
    frete *= random.uniform(0.92, 1.12)

    if ocorrencia == "Atraso":
        frete *= random.uniform(1.02, 1.08)
    elif ocorrencia == "Sinistro":
        frete *= random.uniform(1.05, 1.15)

    return peso_t, round(frete, 2)


def main():
    registros = []
    destinos_lista = list(DESTINOS.keys())
    veiculos_lista = list(VEICULOS.keys())

    for _ in range(N):
        data_embarque = data_aleatoria(DATA_INICIO, DATA_FIM)
        origem = random.choices(ORIGENS, weights=[0.65, 0.35], k=1)[0]
        destino = random.choices(destinos_lista, weights=PESOS_DESTINOS, k=1)[0]
        distancia_km = DESTINOS[destino]

        tipo_veiculo = random.choices(veiculos_lista, weights=PESOS_VEICULOS, k=1)[0]
        transportadora = random.choice(TRANSPORTADORAS)
        ocorrencia = gerar_ocorrencia(distancia_km)

        peso_t, frete_peso = gerar_frete_peso(tipo_veiculo, distancia_km, ocorrencia)
        valor_carga = gerar_valor_carga(tipo_veiculo, peso_t)
        taxa_ad_valorem = gerar_taxa_ad_valorem(valor_carga, distancia_km)

        registros.append(
            [
                data_embarque,
                origem,
                destino,
                valor_carga,
                tipo_veiculo,
                transportadora,
                taxa_ad_valorem,
                frete_peso,
                ocorrencia,
            ]
        )

    registros.sort(key=lambda x: x[0])

    with open(ARQUIVO_SAIDA, "w", newline="", encoding="utf-8-sig") as arquivo:
        writer = csv.writer(arquivo)
        writer.writerow(
            [
                "Data do Embarque",
                "Origem",
                "Destino",
                "Valor da Carga (R$)",
                "Tipo de Veículo",
                "Transportadora",
                "Taxa Ad Valorem (%)",
                "Frete Peso (R$)",
                "Ocorrências",
            ]
        )

        for linha in registros:
            writer.writerow(
                [
                    linha[0].strftime("%d/%m/%Y"),
                    linha[1],
                    linha[2],
                    f"{linha[3]:.2f}",
                    linha[4],
                    linha[5],
                    f"{linha[6]:.4f}",
                    f"{linha[7]:.2f}",
                    linha[8],
                ]
            )

    print(f"Arquivo gerado com sucesso: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
