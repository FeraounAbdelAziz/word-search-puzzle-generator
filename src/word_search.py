from __future__ import annotations


import random
import string
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Set


Direction = Tuple[int, int]


DIRECTIONS: Tuple[Direction, ...] = (
    (0, 1),    # down
    (1, 0),    # right
    (0, -1),   # up
    (-1, 0),   # left
    (1, 1),    # down-right
    (-1, -1),  # up-left
    (1, -1),   # up-right
    (-1, 1),   # down-left
)



@dataclass
class PlacedWord:
    word: str
    path: List[Tuple[int, int]]
    direction_family: str  # "H", "V", or "D"



@dataclass
class WordSearchPuzzle:
    size: int
    words: List[str]
    seed: Optional[int] = None


    grid: List[List[str]] = field(init=False)
    placements: List[PlacedWord] = field(init=False)


    horizontal_used: int = field(init=False)
    vertical_used: int = field(init=False)
    diagonal_used: int = field(init=False)


    def __post_init__(self) -> None:
        # Normalize words (uppercase, no spaces)
        self.words = [w.upper().replace(" ", "") for w in self.words]
        # Empty grid size x size
        self.grid = [["" for _ in range(self.size)] for _ in range(self.size)]
        self.placements = []
        self.random = random.Random(self.seed)


        # Direction usage counters for balanced layout
        self.horizontal_used = 0
        self.vertical_used = 0
        self.diagonal_used = 0


    def _dir_family(self, dx: int, dy: int) -> str:
        if dy == 0 and dx != 0:
            return "H"  # horizontal
        if dx == 0 and dy != 0:
            return "V"  # vertical
        if dx != 0 and dy != 0:
            return "D"  # diagonal
        return "H"


    def generate(self, max_attempts: int = 300) -> None:
        """Generate puzzle with GUARANTEED mix of H/V/D directions."""
        
        # Split words into 3 groups for forced direction distribution
        sorted_words = sorted(self.words, key=len, reverse=True)
        total = len(sorted_words)
        
        # Force distribution: ~40% diagonal, ~30% horizontal, ~30% vertical
        num_diagonal = max(1, (total * 2) // 5)
        num_horizontal = max(1, (total - num_diagonal) // 2)
        num_vertical = total - num_diagonal - num_horizontal
        
        # Assign words to direction groups (longest words get diagonals for better fill)
        diagonal_words = sorted_words[:num_diagonal]
        horizontal_words = sorted_words[num_diagonal:num_diagonal + num_horizontal]
        vertical_words = sorted_words[num_diagonal + num_horizontal:]
        
        # Place each group with STRICT direction enforcement
        for word in diagonal_words:
            placed = self._place_word_strict(word, "D", max_attempts)
            if not placed:
                # Fallback: try any direction if strict fails
                placed = self._place_word(word, max_attempts)
            if not placed:
                raise RuntimeError(f"Unable to place word: {word}")
        
        for word in horizontal_words:
            placed = self._place_word_strict(word, "H", max_attempts)
            if not placed:
                placed = self._place_word(word, max_attempts)
            if not placed:
                raise RuntimeError(f"Unable to place word: {word}")
        
        for word in vertical_words:
            placed = self._place_word_strict(word, "V", max_attempts)
            if not placed:
                placed = self._place_word(word, max_attempts)
            if not placed:
                raise RuntimeError(f"Unable to place word: {word}")
        
        # Fill remaining cells with random letters
        self._fill_random_letters()


    def _place_word_strict(self, word: str, required_family: str, max_attempts: int) -> bool:
        """Place word using ONLY directions from specified family (H/V/D)."""
        coords = [(x, y) for x in range(self.size) for y in range(self.size)]
        
        # Filter directions to only the required family
        allowed_dirs = [d for d in DIRECTIONS if self._dir_family(*d) == required_family]
        
        for _ in range(max_attempts):
            self.random.shuffle(coords)
            self.random.shuffle(allowed_dirs)
            
            for (start_x, start_y) in coords:
                for dx, dy in allowed_dirs:
                    path = self._preview_path(start_x, start_y, dx, dy, word)
                    if not path:
                        continue
                    
                    # Commit letters into grid
                    for (x, y), letter in zip(path, word):
                        self.grid[y][x] = letter
                    
                    fam = self._dir_family(dx, dy)
                    self.placements.append(PlacedWord(word, path, fam))
                    
                    if fam == "H":
                        self.horizontal_used += 1
                    elif fam == "V":
                        self.vertical_used += 1
                    elif fam == "D":
                        self.diagonal_used += 1
                    
                    return True
        
        return False


    def _place_word(self, word: str, max_attempts: int) -> bool:
        """Fallback: place word using any available direction."""
        coords = [(x, y) for x in range(self.size) for y in range(self.size)]


        for _ in range(max_attempts):
            self.random.shuffle(coords)
            directions = list(DIRECTIONS)
            self.random.shuffle(directions)


            usage = {
                "H": self.horizontal_used,
                "V": self.vertical_used,
                "D": self.diagonal_used,
            }


            def _priority(direction: Direction) -> Tuple[int, int]:
                fam = self._dir_family(*direction)
                # Prefer least-used direction family
                if fam == "D":
                    fam_tier = 0
                elif fam == "V":
                    fam_tier = 1
                else:
                    fam_tier = 2
                return fam_tier, usage[fam]


            directions.sort(key=_priority)


            for (start_x, start_y) in coords:
                for dx, dy in directions:
                    path = self._preview_path(start_x, start_y, dx, dy, word)
                    if not path:
                        continue


                    # Commit letters into grid
                    for (x, y), letter in zip(path, word):
                        self.grid[y][x] = letter


                    fam = self._dir_family(dx, dy)
                    self.placements.append(PlacedWord(word, path, fam))


                    if fam == "H":
                        self.horizontal_used += 1
                    elif fam == "V":
                        self.vertical_used += 1
                    elif fam == "D":
                        self.diagonal_used += 1


                    return True


        return False


    def _preview_path(
        self,
        x: int,
        y: int,
        dx: int,
        dy: int,
        word: str,
    ) -> Optional[List[Tuple[int, int]]]:
        path: List[Tuple[int, int]] = []


        for letter in word:
            if not (0 <= x < self.size and 0 <= y < self.size):
                return None


            cell = self.grid[y][x]
            if cell not in ("", letter):
                return None


            path.append((x, y))
            x += dx
            y += dy


        return path


    def _fill_random_letters(self) -> None:
        for y in range(self.size):
            for x in range(self.size):
                if not self.grid[y][x]:
                    self.grid[y][x] = self.random.choice(string.ascii_uppercase)


    def solution_coords(self) -> Set[Tuple[int, int]]:
        result: Set[Tuple[int, int]] = set()
        for placed in self.placements:
            result.update(placed.path)
        return result


    def as_rows(self) -> List[str]:
        return ["".join(row) for row in self.grid]
