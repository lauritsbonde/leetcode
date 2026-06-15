# Usage:
#   make new p=two-sum            scaffold a problem (default Go)
#   make new p=two-sum l=py        scaffold in another language
#   make run d=0001-two-sum        run a Go solution
#   make test d=0001-two-sum       go test a problem dir
#   make py d=0001-two-sum         run the Python solution
#   make submit d=0001-two-sum     submit to LeetCode (needs auth cookies)
#   make submit d=0001-two-sum l=go   submit a specific language
#   make stats                     regenerate the progress table in README.md

.PHONY: new run test py fmt vet submit stats

new:
	python3 fetch.py $(p) $(l)

run:
	go run ./$(d)

test:
	go test ./$(d)

py:
	python3 ./$(d)/solution.py

fmt:
	gofmt -w ./$(d)

vet:
	go vet ./$(d)

submit:
	python3 submit.py $(d) $(l)

stats:
	python3 stats.py
