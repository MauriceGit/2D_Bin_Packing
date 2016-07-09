input=$(./breeder.py --pouch-count 1 5 --pouch-size 10 20 --package-count 10 50 --package-size 5 10 --package-value -20 20 --waste-cost -1 10)
echo "$input"
echo "$input" | ./pwb.py

