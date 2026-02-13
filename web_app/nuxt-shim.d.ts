/// <reference types="nuxt/config" />

declare global {
  const defineNuxtConfig: (config: import('nuxt/config').NuxtConfig) => import('nuxt/config').NuxtConfig
}

export {}
