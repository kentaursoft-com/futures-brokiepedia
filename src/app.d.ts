// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      user?: {
        user: string;
        exp: number;
        iat: number;
      };
    }
    // interface PageData {}
    // interface Platform {}
  }
}

export {};
