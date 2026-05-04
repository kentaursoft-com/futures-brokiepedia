// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      user?: {
        username: string;
        role: string;
        authMethod: string;
        exp: number;
      };
    }
    // interface PageData {}
    // interface Platform {}
  }
}

export {};
