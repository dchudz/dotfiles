declare module 'claude-code' {
  interface PluginState {
    'working-group': {
      /** The sidebar group id to return to when the turn ends; null is Ungrouped. */
      home: string | null
    }
  }
}
