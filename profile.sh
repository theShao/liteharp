sudo python -m cProfile -o fire.prof fire.py 
snakeviz -H 192.168.0.6 fire.prof
