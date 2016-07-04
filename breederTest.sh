input=$(./breeder.py --pouch-count 1 5 --pouch-size 1 20 --package-count 1 50 --package-size 1 20 --package-value -20 20 --waste-cost -10 10)
echo "$input"
echo "$input" | ./pwb.py
