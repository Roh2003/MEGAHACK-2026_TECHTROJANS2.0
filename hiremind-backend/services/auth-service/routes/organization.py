from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status
from pymongo.errors import DuplicateKeyError

from models.organization import Organization
from schemas.organization import (
    OrganizationCreateSchema,
    OrganizationUpdateSchema,
    OrganizationResponseSchema,
)
from shared.response import success
from shared.status_codes import HTTP

router = APIRouter(prefix="/organizations", tags=["Organizations"])


# ── helper ────────────────────────────────────────────────────────────────────

def _serialize(org: Organization) -> dict:
    return {
        "id": str(org.id),
        "organization_id": org.organization_id or str(org.id),
        "name": org.name,
        "industry": org.industry,
        "size": org.size,
        "location": org.location,
        "created_at": org.created_at.isoformat(),
    }


def _generate_next_organization_id(organizations: list[Organization]) -> str:
    next_suffix = 101
    for org in organizations:
        value = (org.organization_id or "").strip()
        if not value.startswith("Org"):
            continue
        suffix = value[3:]
        if suffix.isdigit():
            next_suffix = max(next_suffix, int(suffix) + 1)
    return f"Org{next_suffix}"


async def backfill_missing_organization_ids() -> int:
    docs = await Organization.find(Organization.organization_id == None).sort(Organization.created_at).to_list()
    if not docs:
        return 0

    existing_docs = await Organization.find_all().sort(Organization.created_at).to_list()
    next_suffix = int(_generate_next_organization_id(existing_docs)[3:])
    updated = 0

    for doc in docs:
        doc.organization_id = f"Org{next_suffix}"
        await doc.save()
        next_suffix += 1
        updated += 1

    return updated


async def _get_or_404(org_id: str) -> Organization:
    org = await Organization.find_one(Organization.organization_id == org_id)
    if org:
        return org

    try:
        obj_id = PydanticObjectId(org_id)
    except Exception:
        raise HTTPException(
            status_code=HTTP.BAD_REQUEST,
            detail="Invalid organization ID format",
        )
    org = await Organization.get(obj_id)
    if not org:
        raise HTTPException(
            status_code=HTTP.NOT_FOUND,
            detail=f"Organization '{org_id}' not found",
        )
    return org


# ── CREATE ────────────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_organization(payload: OrganizationCreateSchema):
    """Create a new organization."""
    while True:
        org = Organization(
            organization_id=_generate_next_organization_id(await Organization.find_all().to_list()),
            name=payload.name,
            industry=payload.industry,
            size=payload.size,
            location=payload.location,
        )
        try:
            await org.insert()
            break
        except DuplicateKeyError:
            continue
    return success(data=_serialize(org), message="Organization created successfully", code=HTTP.CREATED)


# ── READ ALL ──────────────────────────────────────────────────────────────────

@router.get("")
async def get_all_organizations():
    """List all organizations, sorted newest first."""
    orgs = await Organization.find_all().sort(-Organization.created_at).to_list()
    return success(data=[_serialize(o) for o in orgs], message="Organizations fetched successfully")


# ── READ BY ID ────────────────────────────────────────────────────────────────

@router.get("/{org_id}")
async def get_organization(org_id: str):
    """Get a single organization by ID."""
    org = await _get_or_404(org_id)
    return success(data=_serialize(org), message="Organization fetched successfully")


# ── UPDATE ────────────────────────────────────────────────────────────────────

@router.put("/{org_id}")
async def update_organization(org_id: str, payload: OrganizationUpdateSchema):
    """Partially update an organization."""
    org = await _get_or_404(org_id)

    update_data = payload.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=HTTP.BAD_REQUEST, detail="No update fields provided")

    for field, value in update_data.items():
        setattr(org, field, value)

    await org.save()
    return success(data=_serialize(org), message="Organization updated successfully")


# ── DELETE ────────────────────────────────────────────────────────────────────

@router.delete("/{org_id}")
async def delete_organization(org_id: str):
    """Delete an organization by ID."""
    org = await _get_or_404(org_id)
    await org.delete()
    return success(data={"organization_id": org.organization_id or org_id}, message="Organization deleted successfully")
