import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.domain import Intervention, Observation, Watershed, FieldPhoto
from app.schemas.schemas import (
    InterventionItem, InterventionCreate, InterventionUpdate,
    ObservationResponse, ObservationCreate, ObservationUpdate
)
from app.core.spatial import validate_coordinates

class InterventionService:
    @staticmethod
    def list_interventions(
        db: Session,
        watershed_id: Optional[int] = None,
        status: Optional[str] = None,
        intervention_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[InterventionItem]:
        """Lists interventions with optional watershed, status, and type filtering."""
        query = db.query(Intervention)
        if watershed_id:
            query = query.filter(Intervention.watershed_id == watershed_id)
        if status:
            query = query.filter(Intervention.status == status.upper())
        if intervention_type:
            query = query.filter(Intervention.intervention_type.ilike(f"%{intervention_type}%"))
            
        interventions = query.order_by(Intervention.id).offset(offset).limit(limit).all()
        return [InterventionItem.model_validate(i) for i in interventions]

    @staticmethod
    def get_intervention_by_id(db: Session, intervention_id: int) -> Optional[InterventionItem]:
        """Retrieves a single intervention by ID."""
        intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
        if not intervention:
            return None
        return InterventionItem.model_validate(intervention)

    @staticmethod
    def create_intervention(db: Session, item_in: InterventionCreate) -> InterventionItem:
        """Creates a new watershed intervention structure record."""
        # Coordinate validation
        valid, err = validate_coordinates(item_in.latitude, item_in.longitude)
        if not valid:
            raise ValueError(err)

        # Check watershed exists
        ws = db.query(Watershed).filter(Watershed.id == item_in.watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed ID {item_in.watershed_id} does not exist.")

        intervention = Intervention(
            watershed_id=item_in.watershed_id,
            code=item_in.code,
            name=item_in.name,
            intervention_type=item_in.intervention_type,
            status=item_in.status.upper(),
            sanction_year=item_in.sanction_year,
            completion_date=item_in.completion_date,
            latitude=item_in.latitude,
            longitude=item_in.longitude,
            target_capacity_cum=item_in.target_capacity_cum,
            beneficiary_count=item_in.beneficiary_count,
            cost_inr=item_in.cost_inr,
            before_metrics=item_in.before_metrics or {},
            after_metrics=item_in.after_metrics or {},
            observed_change_summary=item_in.observed_change_summary,
            source_type=item_in.source_type or "DEMO / SEEDED DATA"
        )
        db.add(intervention)
        db.commit()
        db.refresh(intervention)
        return InterventionItem.model_validate(intervention)

    @staticmethod
    def update_intervention(
        db: Session, 
        intervention_id: int, 
        update_in: InterventionUpdate
    ) -> Optional[InterventionItem]:
        """Updates status, monitoring metrics, or impact observations for an intervention."""
        intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
        if not intervention:
            return None

        if update_in.name is not None:
            intervention.name = update_in.name
        if update_in.status is not None:
            intervention.status = update_in.status.upper()
        if update_in.completion_date is not None:
            intervention.completion_date = update_in.completion_date
        if update_in.target_capacity_cum is not None:
            intervention.target_capacity_cum = update_in.target_capacity_cum
        if update_in.beneficiary_count is not None:
            intervention.beneficiary_count = update_in.beneficiary_count
        if update_in.cost_inr is not None:
            intervention.cost_inr = update_in.cost_inr
        if update_in.before_metrics is not None:
            intervention.before_metrics = update_in.before_metrics
        if update_in.after_metrics is not None:
            intervention.after_metrics = update_in.after_metrics
        if update_in.observed_change_summary is not None:
            intervention.observed_change_summary = update_in.observed_change_summary
        if update_in.source_type is not None:
            intervention.source_type = update_in.source_type

        db.commit()
        db.refresh(intervention)
        return InterventionItem.model_validate(intervention)

    # ----------------- Observation Sub-methods -----------------

    @staticmethod
    def list_observations(
        db: Session,
        watershed_id: Optional[int] = None,
        field_photo_id: Optional[int] = None,
        intervention_id: Optional[int] = None,
        condition_rating: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ObservationResponse]:
        """Lists field observations across watersheds, interventions, or photo records."""
        query = db.query(Observation)
        if watershed_id:
            query = query.filter(Observation.watershed_id == watershed_id)
        if field_photo_id:
            query = query.filter(Observation.field_photo_id == field_photo_id)
        if intervention_id:
            query = query.filter(Observation.intervention_id == intervention_id)
        if condition_rating:
            query = query.filter(Observation.condition_rating == condition_rating.upper())
            
        observations = query.order_by(Observation.observation_date.desc()).offset(offset).limit(limit).all()
        return [ObservationResponse.model_validate(o) for o in observations]

    @staticmethod
    def get_observation_by_id(db: Session, observation_id: int) -> Optional[ObservationResponse]:
        """Retrieves a single observation by ID."""
        obs = db.query(Observation).filter(Observation.id == observation_id).first()
        if not obs:
            return None
        return ObservationResponse.model_validate(obs)

    @staticmethod
    def create_observation(db: Session, obs_in: ObservationCreate) -> ObservationResponse:
        """Records a new qualitative or quantitative field observation."""
        ws = db.query(Watershed).filter(Watershed.id == obs_in.watershed_id).first()
        if not ws:
            raise ValueError(f"Watershed ID {obs_in.watershed_id} does not exist.")

        if obs_in.intervention_id:
            inv = db.query(Intervention).filter(Intervention.id == obs_in.intervention_id).first()
            if not inv:
                raise ValueError(f"Intervention ID {obs_in.intervention_id} does not exist.")

        if obs_in.field_photo_id:
            photo = db.query(FieldPhoto).filter(FieldPhoto.id == obs_in.field_photo_id).first()
            if not photo:
                raise ValueError(f"FieldPhoto ID {obs_in.field_photo_id} does not exist.")

        obs = Observation(
            watershed_id=obs_in.watershed_id,
            field_photo_id=obs_in.field_photo_id,
            intervention_id=obs_in.intervention_id,
            observer_name=obs_in.observer_name,
            observation_date=obs_in.observation_date or datetime.datetime.utcnow(),
            condition_rating=obs_in.condition_rating.upper(),
            remarks=obs_in.remarks,
            recommended_action=obs_in.recommended_action
        )
        db.add(obs)
        db.commit()
        db.refresh(obs)
        return ObservationResponse.model_validate(obs)

    @staticmethod
    def list_observations_for_intervention(
        db: Session, 
        intervention_id: int
    ) -> List[ObservationResponse]:
        """Fetches all observations linked to an intervention."""
        obs = db.query(Observation).filter(Observation.intervention_id == intervention_id).order_by(Observation.observation_date.desc()).all()
        return [ObservationResponse.model_validate(o) for o in obs]
