from typing import Any, Literal
from pydantic import BaseModel, Field


IntentLabel = Literal[
    "cek_stok",
    "minta_rekomendasi",
    "buat_draf_pesanan",
    "tanya_resep_sop",
    "lapor_kendala_stok",
    "di_luar_konteks",
]


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: list[Any] = Field(default_factory=list)


class StandardErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    error: ErrorDetail


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    model_loaded: bool
    model_version: str
    llm_available: bool
    llm_model: str


class IntentRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=3, ge=1, le=6)


class IntentScore(BaseModel):
    intent: IntentLabel
    confidence: float


class IntentResponse(BaseModel):
    status: Literal["success"] = "success"
    intent: IntentLabel
    confidence: float
    needs_clarification: bool
    normalized_text: str
    entities: list[str]
    top_k: list[IntentScore]
    model_version: str
    latency_ms: float


class RestockItemInput(BaseModel):
    id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    unit: str = Field(..., min_length=1)
    current_stock: float = Field(..., ge=0)
    minimum_stock: float = Field(..., ge=0)
    forecast_next_day: float | None = Field(default=None, ge=0)
    lead_time_days: int = Field(default=1, ge=0)
    pack_size: float = Field(default=1.0, gt=0)
    supplier_id: str = Field(default="SUPP-GENERAL")
    supplier_name: str = Field(default="Supplier Hidji")
    supplier_phone: str = Field(default="")


class RestockAdviceRequest(BaseModel):
    date: str = Field(..., min_length=1)
    items: list[RestockItemInput] = Field(..., min_length=1)


class RestockItemAdvice(BaseModel):
    id: str
    name: str
    stock_status: Literal["aman", "menipis", "habis"]
    recommended_qty: int
    unit: str
    affected_menus: list[str]
    reason: str


class WhatsAppDraft(BaseModel):
    supplier_id: str
    supplier_name: str
    message: str
    wa_link: str


class RestockAdviceResponse(BaseModel):
    status: Literal["success"] = "success"
    summary: str
    items: list[RestockItemAdvice]
    drafts: list[WhatsAppDraft]
    fallback_used: bool
    fallback_reason: str | None = None
    model_version: str


class StockSnapshotItem(BaseModel):
    id: str
    name: str
    current_stock: float = Field(..., ge=0)
    minimum_stock: float = Field(..., ge=0)
    unit: str
    status: Literal["aman", "menipis", "habis"] | None = None


class ForecastSnapshotItem(BaseModel):
    id: str
    forecast_next_day: float = Field(..., ge=0)
    unit: str


class ChatRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    stock_snapshot: list[StockSnapshotItem] = Field(default_factory=list)
    forecast: list[ForecastSnapshotItem] = Field(default_factory=list)


class ChatAction(BaseModel):
    type: str
    target: str
    label: str


class ChatResponse(BaseModel):
    status: Literal["success"] = "success"
    intent: IntentLabel
    confidence: float
    answer: str
    sources: list[str]
    actions: list[ChatAction]
    fallback_used: bool
    model_version: str


class ForecastHistoryPoint(BaseModel):
    date: str
    used_qty: float = Field(..., ge=0)


class ForecastMaterialInput(BaseModel):
    material_id: str = Field(..., min_length=1)
    unit: str = Field(..., min_length=1)
    history: list[ForecastHistoryPoint] = Field(default_factory=list)


class ForecastDailyRequest(BaseModel):
    target_date: str = Field(..., min_length=1)
    materials: list[ForecastMaterialInput] = Field(..., min_length=1)


class ForecastPredictionItem(BaseModel):
    material_id: str
    forecast_next_day: float
    unit: str
    baseline_ma7: float


class ForecastDailyResponse(BaseModel):
    status: Literal["success"] = "success"
    target_date: str
    model_version: str
    predictions: list[ForecastPredictionItem]
