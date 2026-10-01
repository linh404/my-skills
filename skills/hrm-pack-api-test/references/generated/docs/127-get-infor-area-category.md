# 127. get_infor_area_category

- Bruno: `Staff Transfer/get_infor_area_category.bru`
- Flow: `staff_transfer`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/area.category/get_infor_area_category`
- Backend model: `area.category`
- Backend method: `get_infor_area_category`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/area_category.py:35`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
