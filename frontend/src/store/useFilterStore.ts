import { create } from "zustand";

interface FilterState {
  startDate: string | null;
  endDate: string | null;
  shift: string;
  hopperId: string;
  setStartDate: (d: string | null) => void;
  setEndDate: (d: string | null) => void;
  setShift: (s: string) => void;
  setHopperId: (h: string) => void;
}

export const useFilterStore = create<FilterState>((set) => ({
  startDate: null,
  endDate: null,
  shift: "All",
  hopperId: "All",
  setStartDate: (d) => set({ startDate: d }),
  setEndDate: (d) => set({ endDate: d }),
  setShift: (s) => set({ shift: s }),
  setHopperId: (h) => set({ hopperId: h }),
}));
