set -e

for f in fixtures/*.json; do

	echo "$f"
	python -m json.tool "$f"
done