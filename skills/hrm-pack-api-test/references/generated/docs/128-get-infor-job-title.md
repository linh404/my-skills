# 128. get_infor_job_title

- Bruno: `Staff Transfer/get_infor_job_title.bru`
- Flow: `staff_transfer`
- Operation: `read`
- Endpoint: `POST {{base_url}}/json/2/hr.job.title/get_infor_job_title`
- Backend model: `hr.job.title`
- Backend method: `get_infor_job_title`
- Source: `/home/linh/vdx/hrm-package/vdx_hr/models/hr_job_title.py:21`
- Evidence: **SOURCE_VERIFIED**

## Must run after
- `Authentication & System/login.bru`
- `Staff Transfer/get_infor_area_category.bru`

## Inputs
Inspect request body

## Captures
none declared

## Constraints and risks
- type/employee/effective date required
- duplicate employee/type/date rejected unless cancelled
