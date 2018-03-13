sudo python -m cProfile -o arrays.prof arrays.py 
snakevis -H 192.168.0.3 arrays.prof
