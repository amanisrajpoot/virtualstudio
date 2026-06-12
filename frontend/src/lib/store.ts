import { create } from 'zustand';

interface AppState {
  isDeveloperMode: boolean;
  toggleDeveloperMode: () => void;
}

export const useAppStore = create<AppState>((set) => ({
  isDeveloperMode: false,
  toggleDeveloperMode: () => set((state) => ({ isDeveloperMode: !state.isDeveloperMode })),
}));
