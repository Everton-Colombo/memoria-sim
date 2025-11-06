import collections
from typing import Dict, List, Tuple

class MemorySimulator:
    def __init__(self, page_size, num_tlb_entries, num_frames, rep_policy):
        self.page_size = page_size
        self.num_tlb_entries = num_tlb_entries
        self.num_frames = num_frames    
        self.rep_policy = rep_policy

        if rep_policy not in ['LRU', 'SecondChance']:
            raise ValueError("Política de substituição inválida. Use 'LRU' ou 'SecondChance'.")

        self.tlb: collections.OrderedDict = collections.OrderedDict()
        self.page_table: Dict[int, int] = {}
        self.frames: List[Tuple[int, int]] = [None] * num_frames

        # contadores de estatísticas
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.page_faults = 0


    def access_memory(self, virtual_address: int) -> None:
        """
        Simula o acesso a um endereço virtual.
        Deve atualizar os contadores e aplicar a política de substituição se necessário.
        """
        
        page_number = virtual_address // self.page_size
        # offset = virtual_address % self.page_size (not used in this simulation)

        # Verify TLB:
        if page_number in self.tlb:
            self.tlb_hits += 1
            frame_number = self.tlb[page_number]
            self.tlb.move_to_end(page_number) # Updates order for LRU
            return
        
        self.tlb_misses += 1

        # Verify Page Table:
        if page_number in self.page_table:
            frame_number = self.page_table[page_number]
            self._update_tlb(page_number, frame_number)
            return

        self.page_faults += 1
        frame_number = self._handle_page_fault(page_number)
        self._update_tlb(page_number, frame_number)
        
    def _update_tlb(self, page_number: int, frame_number: int) -> None:
        """
        Inserts/updates an entry in the TLB using LRU policy.
        """
        
        if page_number in self.tlb:
             self.tlb.move_to_end(page_number)
        else:
            if len(self.tlb) >= self.num_tlb_entries:
                self.tlb.popitem(last=False) # Remove the least recently used entry
            self.tlb[page_number] = frame_number
    
    def _handle_page_fault(self, page_number: int) -> int:
        pass

    def print_statistics(self):
        print("=" * 60)
        print("SIMULADOR DE MEMÓRIA - Estatísticas de Acesso")
        print("=" * 60)
        print(f"Política de Substituição:   {self.replacement_policy}")
        print(f"Tamanho da Página:          {self.page_size} bytes")
        print(f"Entradas na TLB:            {self.num_tlb_entries}")
        print(f"Número de Frames:           {self.num_frames}")
        print("-" * 60)
        print(f"TLB Hits:                   {self.tlb_hits:,}")
        print(f"TLB Misses:                 {self.tlb_misses:,}")
        print(f"Page Faults:                {self.page_faults:,}")
        print("=" * 60)
