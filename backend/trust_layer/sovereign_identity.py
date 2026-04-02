import hashlib
import time
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ed25519

class SovereignIdentity:
    """
    Level 17: Sovereign Identity (DID).
    Establishes BIZIT as a singular, verifiable digital personhood.
    """
    def __init__(self, node_name: str):
        self.node_name = node_name
        # Generate Master Sovereign Keypair
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        self.public_bytes = self.public_key.public_bytes_raw()
        
        # DID: Decentralized Identifier
        self.did = f"did:bizit:{hashlib.sha256(self.public_bytes).hexdigest()[:16]}"
        self.manifestos = []

    def sign_manifesto(self, claim: str):
        """
        Signs a 'Legal Manifesto' or claim using the Sovereign Key.
        """
        timestamp = time.time()
        payload = {
            "did": self.did,
            "claim": claim,
            "timestamp": timestamp,
            "node": self.node_name
        }
        message = json.dumps(payload).encode()
        signature = self.private_key.sign(message)
        
        signed_manifesto = {
            "payload": payload,
            "signature": signature.hex(),
            "attestation": f"BIZIT_SOVEREIGN_ATTESTATION_{int(timestamp)}"
        }
        
        self.manifestos.append(signed_manifesto)
        print(f"⚖️ [SOVEREIGN] Manifesto Signed: {payload['did']} claims '{claim[:30]}...'")
        return signed_manifesto

    def get_identity_doc(self):
        """
        Returns the public 'Identity Document' for the organism.
        """
        return {
            "id": self.did,
            "public_key": self.public_bytes.hex(),
            "controller": self.node_name,
            "verification_method": "Ed25519VerificationKey2020"
        }
