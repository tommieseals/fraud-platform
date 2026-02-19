.PHONY: gen train run dash test clean all

gen:
	python simulator/generate.py

train:
	python training/train.py

run:
	uvicorn scorer.app:app --reload --port 8000

dash:
	streamlit run dashboard/app.py --server.port 8501

test:
	pytest tests/ -v

all: gen train test

clean:
	rm -rf data/*.csv models/*.joblib models/*.json __pycache__ */__pycache__

install:
	pip install -r requirements.txt
