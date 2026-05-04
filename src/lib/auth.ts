// WebAuthn / Passkey Authentication
// Uses SimpleWebAuthn browser client

export interface PasskeyCredential {
  id: string;
  rawId: ArrayBuffer;
  response: AuthenticatorAttestationResponse;
  type: "public-key";
}

export async function registerPasskey(
  challenge: Uint8Array,
  rpName: string,
  rpId: string,
  userId: string,
  userName: string,
): Promise<PasskeyCredential | null> {
  try {
    const credential = await navigator.credentials.create({
      publicKey: {
        challenge: challenge as BufferSource,
        rp: { name: rpName, id: rpId },
        user: {
          id: new TextEncoder().encode(userId),
          name: userName,
          displayName: userName,
        },
        pubKeyCredParams: [
          { alg: -7, type: "public-key" }, // ES256
          { alg: -257, type: "public-key" }, // RS256
        ],
        authenticatorSelection: {
          residentKey: "required",
          userVerification: "required",
        },
        attestation: "none",
      },
    });

    return credential as PasskeyCredential;
  } catch (err) {
    console.error("Passkey registration failed:", err);
    return null;
  }
}

export async function authenticateWithPasskey(
  challenge: Uint8Array,
  rpId: string,
): Promise<PasskeyCredential | null> {
  try {
    const credential = await navigator.credentials.get({
      publicKey: {
        challenge: challenge as BufferSource,
        rpId,
        userVerification: "required",
      },
    });

    return credential as PasskeyCredential;
  } catch (err) {
    console.error("Passkey authentication failed:", err);
    return null;
  }
}
