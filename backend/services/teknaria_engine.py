"""
TEKNARIA ENGINE - Porting from OVERTOP V15
Osservatore → CampoGravitazionale → Ragionatore → Narratore
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Optional
import json

class RegimenType(Enum):
    PROFITABILITY_CRISIS = "PROFITABILITY_CRISIS"
    RECOVERY_STRONG = "RECOVERY_STRONG"
    GROWTH_STABLE = "GROWTH_STABLE"
    COST_PRESSURE = "COST_PRESSURE"
    SEGMENT_DIVERGENCE = "SEGMENT_DIVERGENCE"

class CapsuleType(Enum):
    ALLERTA_REDDITIVITÀ = "ALLERTA_REDDITIVITÀ"
    ALLERTA_CIRCOLARE = "ALLERTA_CIRCOLARE"
    ALLERTA_SEGMENTALE = "ALLERTA_SEGMENTALE"
    OFFENSIVO = "OFFENSIVO"
    DIFENSIVO = "DIFENSIVO"

@dataclass
class Tick:
    """Financial KPI tick."""
    year: int
    revenue_growth: float
    operating_margin: float
    net_margin: float
    cost_of_sales_ratio: float
    metadata: Dict = None

@dataclass
class Capsula:
    """Narrative capsule."""
    tipo: str
    carica: float
    timeline_days: int
    narrativa: str
    azioni: str
    fingerprint_wr: float

class Osservatore:
    """Legge i tick finanziari."""
    
    def __init__(self, dati_bilancio: Dict):
        self.dati = dati_bilancio
        self.ticks: List[Tick] = []
        self._build_ticks()
    
    def _build_ticks(self):
        """Estrae tick da dati bilancio."""
        anni = sorted(self.dati.keys())
        
        for i, anno in enumerate(anni):
            dati_anno = self.dati[anno]
            dati_prev = self.dati[anni[i-1]] if i > 0 else None
            
            if dati_prev:
                revenue_growth = ((dati_anno.get("sales", 0) - dati_prev.get("sales", 0)) / 
                                 dati_prev.get("sales", 1) * 100)
            else:
                revenue_growth = 0
            
            sales = dati_anno.get("sales", 1)
            operating_income = dati_anno.get("operating_income", 0)
            net_income = dati_anno.get("net_income", 0)
            
            tick = Tick(
                year=anno,
                revenue_growth=revenue_growth,
                operating_margin=(operating_income / sales * 100) if sales > 0 else 0,
                net_margin=(net_income / sales * 100) if sales > 0 else 0,
                cost_of_sales_ratio=(dati_anno.get("cogs", 0) / sales * 100) if sales > 0 else 0,
                metadata=dati_anno
            )
            self.ticks.append(tick)

class CampoGravitazionale:
    """Calcola forze che muovono il segnale."""
    
    def __init__(self, osservatore: Osservatore):
        self.osservatore = osservatore
        self.ticks = osservatore.ticks
    
    def calculate_seed(self) -> float:
        """Solidità patrimoniale."""
        if not self.ticks:
            return 0.5
        latest = self.ticks[-1]
        return 0.7 if latest.net_margin > 0 else 0.3
    
    def calculate_fingerprint_wr(self) -> float:
        """Historical win rate (stub)."""
        return 0.85
    
    def calculate_momentum(self) -> float:
        """Trend."""
        if len(self.ticks) < 2:
            return 0.5
        margins = [t.operating_margin for t in self.ticks]
        avg = sum(margins) / len(margins)
        trend = (margins[-1] - margins[0]) / abs(margins[0]) if margins[0] != 0 else 0
        return min(1.0, max(0.0, trend))
    
    def calculate_volatility(self) -> float:
        """Margin variability."""
        if len(self.ticks) < 2:
            return 0.3
        margins = [t.operating_margin for t in self.ticks]
        avg = sum(margins) / len(margins)
        variance = sum((m - avg) ** 2 for m in margins) / len(margins)
        std_dev = variance ** 0.5
        return (std_dev / avg) if avg > 0 else 0.3
    
    def calculate_regime(self) -> str:
        """Current regime."""
        if not self.ticks:
            return RegimenType.GROWTH_STABLE.value
        latest = self.ticks[-1]
        if latest.net_margin < 0:
            return RegimenType.PROFITABILITY_CRISIS.value
        elif latest.operating_margin > 5:
            return RegimenType.GROWTH_STABLE.value
        else:
            return RegimenType.COST_PRESSURE.value

class Ragionatore:
    """Genera capsule."""
    
    def __init__(self, osservatore: Osservatore, campo: CampoGravitazionale):
        self.osservatore = osservatore
        self.campo = campo
        self.capsule: List[Capsula] = []
    
    def ragiona(self):
        """Analizza e genera capsule."""
        ticks = self.osservatore.ticks
        if not ticks:
            return
        
        if len(ticks) >= 2:
            latest = ticks[-1]
            prev = ticks[-2]
            
            if latest.operating_margin > prev.operating_margin:
                self._capsula_positive()
            else:
                self._capsula_warning()
        
        self._capsula_cost_pressure()
    
    def _capsula_positive(self):
        """Capsula positiva."""
        c = Capsula(
            tipo=CapsuleType.OFFENSIVO.value,
            carica=0.75,
            timeline_days=180,
            narrativa="Trend operativo positivo. Margini in miglioramento.",
            azioni="Mantenere focus su profittabilità. Investire strategicamente.",
            fingerprint_wr=0.88
        )
        self.capsule.append(c)
    
    def _capsula_warning(self):
        """Capsula warning."""
        c = Capsula(
            tipo=CapsuleType.DIFENSIVO.value,
            carica=0.65,
            timeline_days=270,
            narrativa="Pressione sui margini operativi. Monitorare costi.",
            azioni="Analizzare struttura costi. Valutare efficienze.",
            fingerprint_wr=0.82
        )
        self.capsule.append(c)
    
    def _capsula_cost_pressure(self):
        """Capsula pressione costi."""
        c = Capsula(
            tipo=CapsuleType.ALLERTA_REDDITIVITÀ.value,
            carica=0.68,
            timeline_days=365,
            narrativa="Precursori di compressione margin emergeranno 9-12 mesi.",
            azioni="Monitora ratio operativi trimestralmente.",
            fingerprint_wr=0.80
        )
        self.capsule.append(c)

class Narratore:
    """Trasforma in story."""
    
    def __init__(self, ragionatore: Ragionatore):
        self.ragionatore = ragionatore
    
    def narra(self) -> str:
        """Genera narrativa."""
        ticks = self.ragionatore.osservatore.ticks
        if not ticks:
            return "Dati insufficienti per analisi."
        
        narrative = "HERMENEUTICA - LETTURA DEL BILANCIO\n"
        narrative += "=" * 60 + "\n\n"
        
        for tick in ticks:
            narrative += f"ANNO {tick.year}:\n"
            narrative += f"  Crescita fatturato: {tick.revenue_growth:+.1f}%\n"
            narrative += f"  Margine operativo: {tick.operating_margin:.2f}%\n"
            narrative += f"  Margine netto: {tick.net_margin:.2f}%\n"
            narrative += f"  Costi: {tick.cost_of_sales_ratio:.1f}% fatturato\n\n"
        
        latest = ticks[-1]
        if latest.net_margin < 0:
            narrative += "⚠️ ANALISI: Azienda in perdita. Revire necessaria.\n"
        elif latest.operating_margin < 5:
            narrative += "⚠️ ANALISI: Margini sotto 5%. Pressione sui costi visibile.\n"
        else:
            narrative += "✅ ANALISI: Situazione stabile. Margini sani.\n"
        
        narrative += "\nCAPSULE GENERATE:\n"
        for i, cap in enumerate(self.ragionatore.capsule, 1):
            narrative += f"\n{i}. {cap.tipo} (carica: {cap.carica:.2f})\n"
            narrative += f"   {cap.narrativa}\n"
            narrative += f"   Azioni: {cap.azioni}\n"
        
        return narrative

class TeknariaEngine:
    """Orquestration."""
    
    def __init__(self, dati_bilancio: Dict):
        self.dati = dati_bilancio
        self.osservatore = Osservatore(dati_bilancio)
        self.campo = CampoGravitazionale(self.osservatore)
        self.ragionatore = Ragionatore(self.osservatore, self.campo)
        self.narratore = Narratore(self.ragionatore)
    
    def analyze(self) -> List[Dict]:
        """Lancia analisi, ritorna capsule."""
        self.ragionatore.ragiona()
        return [
            {
                "tipo": c.tipo,
                "carica": c.carica,
                "timeline_days": c.timeline_days,
                "narrativa": c.narrativa,
                "azioni": c.azioni,
                "fingerprint_wr": c.fingerprint_wr
            }
            for c in self.ragionatore.capsule
        ]
    
    def generate_narrative(self) -> str:
        """Genera storia."""
        return self.narratore.narra()
