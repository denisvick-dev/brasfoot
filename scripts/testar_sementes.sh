#!/usr/bin/env bash
# Roda a suíte com várias sementes (o "universo" de cada execução).
#
# Uso:
#   bash scripts/testar_sementes.sh            # sementes 1..5
#   bash scripts/testar_sementes.sh 10 20 30   # sementes escolhidas
#   bash scripts/testar_sementes.sh $(seq 1 50)
#
# Cada falha vira uma anotação do GitHub (`::error title=...`), para não depender
# do log do runner. O XML do JUnit é temporário e não fica no repositório.
set -uo pipefail

# Em CI o `pytest` está no PATH; localmente pode ser preciso apontar o do venv:
#   PYTEST=.venv/bin/pytest bash scripts/testar_sementes.sh
pytest_cmd=${PYTEST:-pytest}

sementes=("$@")
if [ ${#sementes[@]} -eq 0 ]; then
    sementes=(1 2 3 4 5)
fi

xml_dir=$(mktemp -d)
trap 'rm -rf "$xml_dir"' EXIT

falhas=()

for s in "${sementes[@]}"; do
    echo "::group::semente $s"
    xml="$xml_dir/semente-$s.xml"
    if BRASFOOT_SEED=$s "$pytest_cmd" -q --no-header -p no:cacheprovider --junitxml="$xml"; then
        echo "semente $s: ok"
    else
        falhas+=("$s")
        # Lista os testes que quebraram direto na anotação (o log do runner fica
        # num blob que nem sempre é acessível de fora do GitHub).
        python - "$s" "$xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

semente, caminho = sys.argv[1], sys.argv[2]
try:
    raiz = ET.parse(caminho).getroot()
except (OSError, ET.ParseError):
    print(f"::error title=Semente {semente}::falhou (sem XML do JUnit)")
    raise SystemExit(0)

quebrados = [
    caso for caso in raiz.iter("testcase")
    if caso.find("failure") is not None or caso.find("error") is not None
]
if not quebrados:
    print(f"::error title=Semente {semente}::falhou sem teste quebrado (erro na coleta?)")
for caso in quebrados:
    nome = f"{caso.get('classname')}::{caso.get('name')}"
    print(f"::error title=Semente {semente}::{nome}")
PY
        echo "semente $s: FALHOU (BRASFOOT_SEED=$s pytest para reproduzir)"
    fi
    echo "::endgroup::"
done

if [ ${#falhas[@]} -gt 0 ]; then
    echo "::error title=Sementes com falha::${falhas[*]}"
    echo "sementes com falha: ${falhas[*]}"
    exit 1
fi

echo "todas as sementes passaram: ${sementes[*]}"
