Run the Script:

Use the following command to run the script:

python qkd.py -q 10 -v

The -q argument specifies the number of qubits (adjust 10 as needed).
The -v flag enables verbose output to show detailed logs.

If you want to simulate an eavesdropper (Eve), add the --eve flag:

python qkd.py -q 10 -v --eve
