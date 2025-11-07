import collections
from typing import Dict, List, Tuple, Optional, Literal

class MemorySimulator:
    def __init__(self, page_size: int, num_tlb_entries: int, num_frames: int, rep_policy: Literal['LRU', 'SecondChance'], debug: bool = False):
        self.debug = debug
        
        self.page_size = page_size
        self.num_tlb_entries = num_tlb_entries
        self.num_frames = num_frames    
        self.rep_policy = rep_policy

        if rep_policy not in ['LRU', 'SecondChance']:
            raise ValueError("Política de substituição inválida. Use 'LRU' ou 'SecondChance'.")

        self.tlb: collections.OrderedDict = collections.OrderedDict() # Dict[int, int] -> page_number: frame_number
        self.page_table: collections.OrderedDict = collections.OrderedDict() # Dict[int, int] -> page_number: frame_number
        self.frames: List[Optional[int]] = [None] * num_frames # frames[frame_number] = page_number

        # contadores de estatísticas
        self.tlb_hits = 0
        self.tlb_misses = 0
        self.page_faults = 0


    def access_memory(self, virtual_address: int) -> None:
        """
        Simula o acesso a um endereço virtual.
        Deve atualizar os contadores e aplicar a política de substituição se necessário.
        """
        
        if self.debug:
            print(f"Acessando endereço virtual: {virtual_address}")
        
        page_number = virtual_address // self.page_size
        # offset = virtual_address % self.page_size (not used in this simulation)

        # Verify TLB:
        if page_number in self.tlb:
            if self.debug:
                print(f"TLB Hit para a página {page_number}")
            
            self.tlb_hits += 1
            frame_number = self.tlb[page_number]
            # Update order for LRU:
            self.tlb.move_to_end(page_number) 
            self.page_table.move_to_end(page_number)
            return
        
        if self.debug:
            print(f"TLB Miss para a página {page_number}")
        self.tlb_misses += 1

        # Verify Page Table:
        if page_number in self.page_table:
            if self.debug:
                print(f"Page Table Hit para a página {page_number}")
            
            frame_number = self.page_table[page_number]
            self.page_table.move_to_end(page_number) # Update order for LRU
            self._update_tlb(page_number, frame_number)
            return

        if self.debug:
            print(f"Page Fault para a página {page_number}")
        self.page_faults += 1
        frame_number = self._handle_page_fault(page_number)
        self._update_tlb(page_number, frame_number)
        self.access_memory(virtual_address)  # Retry access after handling page fault
        
    def _update_tlb(self, page_number: int, frame_number: int) -> None:
        """
        Inserts/updates an entry in the TLB using LRU policy.
        """
        if len(self.tlb) >= self.num_tlb_entries:
            self.tlb.popitem(last=False) # Remove the least recently used entry
        self.tlb[page_number] = frame_number
    
    def _allocate_frame(self) -> Optional[int]:
        """
        Finds a free frame. Returns the frame number or None if all frames are occupied.
        """
        for i in range(self.num_frames):
            if self.frames[i] is None:
                return i
        return None
    
    def _handle_page_fault(self, page_number: int) -> int:
        """
        Handles a page fault. Finds a free frame or applies the replacement policy.
        
        Returns the frame number where the page is loaded.
        """
        
        frame_number = self._allocate_frame()
        
        if frame_number is None:
            if self.rep_policy == 'LRU':
                frame_number = self._find_victim_lru()
            elif self.rep_policy == 'SecondChance':
                frame_number = self._find_victim_second_chance()
        
        self.frames[frame_number] = page_number
        self.page_table[page_number] = frame_number
        self._update_tlb(page_number, frame_number)
    
    def _find_victim_lru(self) -> int:
        """selects a victim page using LRU policy and returns its frame number."""

        victim_page, frame_to_evict = self.page_table.popitem(last=False) # First entry is the LRU

        if victim_page in self.tlb:
            del self.tlb[victim_page]
        
        if self.debug:
            print(f"LRU: Removendo página {victim_page} do frame {frame_to_evict}")
        
        return frame_to_evict

    def _find_victim_second_chance(self) -> int:
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
