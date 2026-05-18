"""
to run fastapi
python -m uvicorn api.main:app --reload

to run cli
python -m app.chat


to test health
curl http://localhost:8000/api/health

to give prompt (single query)

curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "what is a queue?"}'

to give multi query (async)
for i in {1..5}; do
  (time curl -X POST http://localhost:8000/api/chat \
    -H "Content-Type: application/json" \
    -d '{"query": "what is a queue?"}') &
done
wait

seq 1 500 | xargs -I{} -P25 curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query":"what is a queue?"}'



  different questions
  questions=(
"What is a stack?"
"Explain binary search."
"What is a linked list?"
"Explain recursion."
"What is hashing?"
)

export questions

seq 1 500 | xargs -I{} -P25 bash -c '
arr=(
"What is a stack?"
"Explain binary search."
"What is a linked list?"
"Explain recursion."
"What is hashing?"
)

q=${arr[$RANDOM % ${#arr[@]}]}

curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"$q\"}"
'
"""

