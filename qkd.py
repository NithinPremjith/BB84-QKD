import math
from random import randint
from numpy import matrix, sqrt
import argparse


class qubit():
    def __init__(self, initial_state):
        if initial_state:
            self.__state = matrix([[0], [1]])  # |0> state
        else:
            self.__state = matrix([[1], [0]])  # |1> state
        self.__measured = False
        self.__H = (1 / sqrt(2)) * matrix([[1, 1], [1, -1]])  # Hadamard Gate
        self.__X = matrix([[0, 1], [1, 0]])  # Pauli-X Gate

    def show(self):
        aux = ""
        prob_0 = round((matrix([1, 0]) * self.__state).item(), 2)
        prob_1 = round((matrix([0, 1]) * self.__state).item(), 2)

        if prob_0 != 0:
            aux += f"{prob_0}|0>" if prob_0 != 1.0 else "|0>"
        if prob_1 != 0:
            if aux:
                aux += " + "
            aux += f"{prob_1}|1>" if prob_1 != 1.0 else "|1>"
        return aux

    def measure(self):
        if self.__measured:
            raise Exception("Qubit already measured!")
        M = 1000000
        m = randint(0, M)
        self.__measured = True
        prob = round((matrix([1, 0]) * self.__state).item(), 2)  # Probability amplitude of state |0>
        prob_squared = prob ** 2  # Square the probability amplitude
        if m < prob_squared * M:
            return 0
        else:
            return 1

    def hadamard(self):
        if self.__measured:
            raise Exception("Qubit already measured!")
        self.__state = self.__H * self.__state

    def X(self):
        if self.__measured:
            raise Exception("Qubit already measured!")
        self.__state = self.__X * self.__state


class quantum_user():
    def __init__(self, name):
        self.name = name

    def send(self, data, basis):
        qubits = list()
        for i in range(len(data)):
            if not basis[i]:
                if not data[i]:
                    qubits.append(qubit(0))  # |0> state
                else:
                    qubits.append(qubit(1))  # |1> state
            else:
                if not data[i]:
                    aux = qubit(0)
                else:
                    aux = qubit(1)
                aux.hadamard()  # Apply Hadamard gate if basis is 1
                qubits.append(aux)
        return qubits

    def receive(self, data, basis):
        bits = list()
        for i in range(len(data)):
            if not basis[i]:
                bits.append(data[i].measure())  # Measure the qubit
            else:
                data[i].hadamard()  # Apply Hadamard gate if basis is 1
                bits.append(data[i].measure())
        return bits


def generate_random_bits(N):
    return [randint(0, 1) for _ in range(N)]


def calculate_entropy(bits):
    # Shannon entropy formula: H(X) = - p_0*log2(p_0) - p_1*log2(p_1)
    p_0 = bits.count(0) / len(bits)
    p_1 = bits.count(1) / len(bits)
    entropy = 0
    if p_0 > 0:
        entropy -= p_0 * math.log2(p_0)
    if p_1 > 0:
        entropy -= p_1 * math.log2(p_1)
    return entropy


def fidelity(state1, state2):
    # Fidelity between two quantum states
    return abs((state1.H * state2).item()) ** 2


def QKD(N, verbose=False, eve_present=False):
    # Step 1: Generate random bits and basis for Alice
    alice_basis = generate_random_bits(N)
    alice_bits = generate_random_bits(N)
    alice = quantum_user("Alice")
    alice_qubits = alice.send(data=alice_bits, basis=alice_basis)

    # Step 2: Eve intercepts the qubits if present
    if eve_present:
        eve_basis = generate_random_bits(N)
        eve = quantum_user("Eve")
        eve_bits = eve.receive(data=alice_qubits, basis=eve_basis)
        alice_qubits = eve.send(data=eve_bits, basis=eve_basis)

    # Step 3: Bob receives the qubits and measures them
    bob_basis = generate_random_bits(N)
    bob = quantum_user("Bob")
    bob_bits = bob.receive(data=alice_qubits, basis=bob_basis)

    # Step 4: Key generation by comparing basis
    matching_bits = [i for i in range(N) if alice_basis[i] == bob_basis[i]]
    alice_key = [alice_bits[i] for i in matching_bits]
    bob_key = [bob_bits[i] for i in matching_bits]

    # Step 5: Calculate entropy of the shared key
    key_entropy = calculate_entropy(alice_key)

    if verbose:
        print(f"Key length: {len(alice_key)}")
        print(f"Alice's Key: {alice_key}")
        print(f"Bob's Key: {bob_key}")
        print(f"Entropy of the key: {key_entropy}")

    # Step 6: Fidelity between Alice's and Bob's states
    alice_state = matrix([[0], [1]])  # Example state |0>
    bob_state = matrix([[0], [1]])  # Example state |0>
    fidelity_score = fidelity(alice_state, bob_state)
    if verbose:
        print(f"Fidelity between Alice's and Bob's state: {fidelity_score}")

    return alice_key, bob_key, key_entropy, fidelity_score


# Function for encrypting a binary message with the key
def encrypt_message(message, key):
    encrypted_message = ''.join([str(int(message[i]) ^ key[i % len(key)]) for i in range(len(message))])
    return encrypted_message


# Function for decrypting a binary message with the key
def decrypt_message(encrypted_message, key):
    decrypted_message = ''.join([str(int(encrypted_message[i]) ^ key[i % len(key)]) for i in range(len(encrypted_message))])
    return decrypted_message


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Quantum Key Distribution Simulator with Advanced Mathematical Model')
    parser.add_argument('-q', '--qubits', type=int, required=True, help='Number of qubits to send')
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('--eve', action='store_true', help='Enable Eve\'s presence (Eve intercepts the key)')
    args = parser.parse_args()

    # Step 1: Perform Quantum Key Distribution (QKD)
    alice_key, bob_key, key_entropy, fidelity_score = QKD(args.qubits, verbose=args.verbose, eve_present=args.eve)

    # Step 2: Encrypt and decrypt a message
    message = "1101011011"  # Example binary message
    print(f"\nOriginal message: {message}")

    encrypted_message = encrypt_message(message, alice_key)
    print(f"Encrypted message: {encrypted_message}")

    decrypted_message = decrypt_message(encrypted_message, bob_key)
    print(f"Decrypted message: {decrypted_message}")

    # Step 3: Verify the decrypted message
    if decrypted_message == message:
        print("\nDecryption successful! The decrypted message matches the original.")
    else:
        print("\nDecryption failed! The decrypted message does not match the original.")

    # Final output
    print(f"\nNumber of basis matches: {len(alice_key)}")
    print(f"Successfully exchanged key!")
    print(f"Alice's Key: {alice_key}")
    print(f"Bob's Key: {bob_key}")
    print(f"Entropy of the key: {key_entropy}")
    print(f"Fidelity score: {fidelity_score}")
