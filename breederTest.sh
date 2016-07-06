input=$(./breeder.py --pouch-count 50 50 --pouch-size 10 20 --package-count 2000 2000 --package-size 5 10 --package-value -20 20 --waste-cost -1 10)
echo "$input"
echo "$input" | ./pwb.py

