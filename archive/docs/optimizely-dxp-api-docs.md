# Optimizely DXP Deployment API - Complete Documentation

## Overview

The Optimizely Digital Experience Platform (DXP) Deployment API is a REST API that enables CI/CD workflows for deploying applications to DXP environments. This documentation compiles information from official sources, PowerShell module implementations, and community resources.

**Base URL:** `https://paasportal.episerver.net/api/v1.0/`

**API Version:** v1.0

## Authentication

### Creating API Credentials

1. Navigate to the DXP Management Portal at `https://paasportal.episerver.net`
2. Go to the **API** tab
3. Click **Add API credentials**
4. Enter a name and select environment permissions
5. Copy the **ClientKey** and **ClientSecret** (secret shown only once)

### HMAC Authentication

All API requests must be authenticated using HMAC-SHA256 signatures.

#### Authorization Header Format

```
Authorization: epi-hmac {api-key}:{timestamp}:{nonce}:{hmac}
```

#### HMAC Computation Process

1. **Assemble the message** by concatenating:
   - API Key
   - HTTP method (uppercase, e.g., "POST")
   - Request target (path + query string)
   - Timestamp (UTC milliseconds from Unix epoch)
   - Nonce (random unique identifier)
   - MD5 hash of request body (Base64-encoded)

2. **Compute HMAC**:
   - Hash the message using HMAC-SHA256
   - Use the API Secret (Base64-decoded) as the key
   - Convert result to Base64 string

#### C# Example

```csharp
var hmacAlgorithm = new HMACSHA256();
var md5 = MD5.Create();

// Set the secret
hmacAlgorithm.Key = Convert.FromBase64String(clientSecret);

// Build signature components
var timestamp = DateTimeOffset.UtcNow.ToUnixTimeMilliseconds();
var nonce = Guid.NewGuid().ToString("N");
var target = new Uri(apiUrl).PathAndQuery;

// Hash request body
byte[] bodyBytes = body != null 
    ? Encoding.UTF8.GetBytes(JsonSerializer.Serialize(body)) 
    : Encoding.UTF8.GetBytes("");
var bodyHashBytes = md5.ComputeHash(bodyBytes);
var hashBody = Convert.FromBase64String(bodyHashBytes);

// Create signature message
var message = $"{clientKey}{method.ToUpper()}{target}{timestamp}{nonce}{hashBody}";
var messageBytes = Encoding.UTF8.GetBytes(message);

// Compute HMAC signature
var signatureHash = hmacAlgorithm.ComputeHash(messageBytes);
var signature = Convert.ToBase64String(signatureHash);

// Build authorization header
var authorization = $"epi-hmac {clientKey}:{timestamp}:{nonce}:{signature}";
```

#### JavaScript/Node.js Example (Postman Pre-Request)

```javascript
var crypto = require("crypto-js");
var sdk = require('postman-collection');

var method = pm.request.method;
var key = pm.variables.get("ClientKey");
var secret = CryptoJS.enc.Base64.parse(pm.variables.get("ClientSecret"));
var target = new sdk.Url(request.url).getPathWithQuery();
var timestamp = (new Date()).getTime();
var nonce = Math.random().toString(36).substring(7);

var body = pm.request.body ? pm.request.body.raw : "";
var bodybase64 = crypto.MD5(body).toString(CryptoJS.enc.Base64);

var hmac = crypto.HmacSHA256(
    key + method + target + timestamp + nonce + bodybase64, 
    secret
);
var base64hmac = CryptoJS.enc.Base64.stringify(hmac);

var header = "epi-hmac " + key + ":" + timestamp + ":" + nonce + ":" + base64hmac;
pm.request.headers.add(header, "Authorization");
```

---

## API Endpoints

### Deployment Operations

#### 1. Start Code Package Deployment

**Endpoint:** `POST /projects/{projectId}/deployments`

**Description:** Deploys a NuGet package to a target environment.

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID

**Request Body:**

```json
{
  "deploymentPackage": "myapp.cms.app.1.0.0.nupkg",
  "targetEnvironment": "Integration",
  "useMaintenancePage": false,
  "directDeploy": false
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `deploymentPackage` | string | Yes | Package filename (must follow naming convention) |
| `targetEnvironment` | string | Yes | "Integration", "Preproduction", or "Production" |
| `useMaintenancePage` | boolean | No | Enable maintenance page during deployment (default: false) |
| `directDeploy` | boolean | No | Deploy directly to production slot (Integration only, default: false) |
| `zeroDowntimeMode` | string | No | "ReadOnly" or "ReadWrite" for zero downtime deployments |

**Response:** `200 OK`

```json
{
  "id": "2a52c873-b39c-4f44-b842-aab5009c3060",
  "projectId": "2a561398-d517-4634-9bc4-aab5008a8e1a",
  "status": "InProgress",
  "startTime": "2025-10-10T09:28:39.479Z",
  "endTime": null,
  "percentComplete": 0,
  "validationLinks": [],
  "deploymentErrors": [],
  "deploymentWarnings": [],
  "parameters": {
    "targetEnvironment": "Integration",
    "packages": ["myapp.cms.app.1.0.0.nupkg"],
    "maintenancePage": false,
    "directDeploy": false
  }
}
```

---

#### 2. Start Source Environment Deployment

**Endpoint:** `POST /projects/{projectId}/deployments`

**Description:** Deploys code from one environment to another (e.g., Integration → Preproduction).

**Request Body:**

```json
{
  "sourceEnvironment": "Integration",
  "targetEnvironment": "Preproduction",
  "sourceApp": ["cms", "commerce"],
  "includeBlob": false,
  "includeDb": false,
  "useMaintenancePage": false,
  "zeroDowntimeMode": "ReadOnly"
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `sourceEnvironment` | string | Yes | Source environment name |
| `targetEnvironment` | string | Yes | Target environment name |
| `sourceApp` | array | No | Apps to deploy: ["cms"], ["commerce"], or ["cms", "commerce"] |
| `includeBlob` | boolean | No | Copy BLOB storage (default: false) |
| `includeDb` | boolean | No | Copy database (default: false) |
| `useMaintenancePage` | boolean | No | Enable maintenance page (default: false) |
| `zeroDowntimeMode` | string | No | "ReadOnly" or "ReadWrite" |

**Response:** Same as Start Code Package Deployment

---

#### 3. Get Deployment Status

**Endpoint:** `GET /projects/{projectId}/deployments/{deploymentId}`

**Description:** Retrieves the status of a specific deployment.

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID
- `deploymentId` (string, required): Deployment UUID

**Response:** `200 OK`

```json
{
  "id": "2a52c873-b39c-4f44-b842-aab5009c3060",
  "projectId": "2a561398-d517-4634-9bc4-aab5008a8e1a",
  "status": "AwaitingVerification",
  "startTime": "2025-10-10T09:28:39.479Z",
  "endTime": null,
  "percentComplete": 100,
  "validationLinks": [
    "https://myapp-inte-slot.azurewebsites.net"
  ],
  "deploymentErrors": [],
  "deploymentWarnings": [],
  "parameters": {
    "targetEnvironment": "Integration",
    "packages": ["myapp.cms.app.1.0.0.nupkg"],
    "maintenancePage": false
  }
}
```

**Deployment Status Values:**
- `InProgress` - Deployment is running
- `AwaitingVerification` - Deployed to slot, awaiting manual verification
- `Succeeded` - Deployment completed successfully
- `Failed` - Deployment failed
- `ResetInProgress` - Deployment reset in progress
- `Redeployed` - Deployment was rolled back

---

#### 4. List Deployments

**Endpoint:** `GET /projects/{projectId}/deployments`

**Description:** Lists recent deployments for a project.

**Query Parameters:**
- `limit` (integer, optional): Max results (default: 20, max: 100)
- `offset` (integer, optional): Pagination offset (default: 0)

**Response:** `200 OK`

```json
[
  {
    "id": "deployment-id-1",
    "projectId": "project-uuid",
    "status": "Succeeded",
    "startTime": "2025-10-10T09:28:39.479Z",
    "endTime": "2025-10-10T09:45:12.321Z",
    "percentComplete": 100,
    "parameters": {
      "targetEnvironment": "Integration"
    }
  },
  ...
]
```

---

#### 5. Complete Deployment

**Endpoint:** `POST /projects/{projectId}/deployments/{deploymentId}/complete`

**Description:** Completes a deployment in verification stage (swaps slot to production).

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID
- `deploymentId` (string, required): Deployment UUID

**Request Body:** Empty (`{}`)

**Response:** `200 OK`

```json
{
  "id": "2a52c873-b39c-4f44-b842-aab5009c3060",
  "status": "Succeeded",
  "message": "Deployment completed successfully"
}
```

---

#### 6. Reset Deployment

**Endpoint:** `POST /projects/{projectId}/deployments/{deploymentId}/reset`

**Description:** Resets/cancels a deployment in verification stage (rollback).

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID
- `deploymentId` (string, required): Deployment UUID

**Request Body (Optional):**

```json
{
  "rollbackDatabase": true,
  "validateBeforeSwap": true
}
```

**Response:** `200 OK`

```json
{
  "id": "2a52c873-b39c-4f44-b842-aab5009c3060",
  "status": "ResetInProgress",
  "message": "Deployment reset initiated"
}
```

---

### Database Operations

#### 7. Start Database Export

**Endpoint:** `POST /projects/{projectId}/environments/{environment}/databases/{databaseName}/exports`

**Description:** Exports a database as a .bacpac file.

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID
- `environment` (string, required): "Integration", "Preproduction", or "Production"
- `databaseName` (string, required): "epicms" or "epicommerce"

**Request Body:**

```json
{
  "retentionHours": 168
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `retentionHours` | integer | No | Hours to retain export (default: 168 = 7 days) |

**Response:** `200 OK`

```json
{
  "id": "export-uuid",
  "projectId": "project-uuid",
  "environment": "Integration",
  "databaseName": "epicms",
  "status": "InProgress",
  "percentComplete": 0,
  "downloadLink": null,
  "expiresAt": "2025-10-17T10:00:00.000Z"
}
```

---

#### 8. Get Database Export Status

**Endpoint:** `GET /projects/{projectId}/environments/{environment}/databases/{databaseName}/exports/{exportId}`

**Description:** Retrieves the status of a database export.

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID
- `environment` (string, required): Environment name
- `databaseName` (string, required): Database name
- `exportId` (string, required): Export UUID

**Response:** `200 OK`

```json
{
  "id": "export-uuid",
  "projectId": "project-uuid",
  "environment": "Integration",
  "databaseName": "epicms",
  "status": "Succeeded",
  "percentComplete": 100,
  "downloadLink": "https://storage.blob.core.windows.net/exports/epicms-20251010.bacpac?sv=...",
  "expiresAt": "2025-10-17T10:00:00.000Z",
  "fileSizeBytes": 524288000
}
```

**Export Status Values:**
- `InProgress` - Export is running
- `Succeeded` - Export completed, download link available
- `Failed` - Export failed

---

### Storage Container Operations

#### 9. List Storage Containers

**Endpoint:** `GET /projects/{projectId}/environments/{environment}/storagecontainers`

**Description:** Lists available BLOB storage containers in an environment.

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID
- `environment` (string, required): Environment name

**Response:** `200 OK`

```json
[
  {
    "name": "mysitemedia",
    "containerType": "Blob",
    "created": "2023-01-15T10:00:00.000Z"
  },
  {
    "name": "mysiteassets",
    "containerType": "Blob",
    "created": "2023-01-15T10:00:00.000Z"
  }
]
```

---

#### 10. Generate Storage Container SAS Link

**Endpoint:** `POST /projects/{projectId}/environments/{environment}/storagecontainers/{containerName}/saslink`

**Description:** Generates a read-only SAS (Shared Access Signature) link to access container contents.

**Path Parameters:**
- `projectId` (string, required): DXP Project UUID
- `environment` (string, required): Environment name
- `containerName` (string, required): Container name

**Request Body:**

```json
{
  "expiryHours": 24,
  "permissions": "Read"
}
```

**Request Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `expiryHours` | integer | No | Hours until link expires (default: 24) |
| `permissions` | string | No | "Read", "Write", "Delete", or "List" (default: "Read") |

**Response:** `200 OK`

```json
{
  "sasLink": "https://mystorageaccount.blob.core.windows.net/mysitemedia?sv=2021-08-06&ss=b&srt=sco&sp=r&se=2025-10-11T10:00:00Z&st=2025-10-10T10:00:00Z&spr=https&sig=...",
  "expiresAt": "2025-10-11T10:00:00.000Z"
}
```

---

## Code Package Format

### Naming Convention

Code packages must follow this naming pattern:

```
[app-name].<package-type>.app.<version>.nupkg
```

**Examples:**
- `mysite.cms.app.1.0.0.nupkg`
- `cms.app.1.2.5.nupkg`
- `mysite.commerce.app.2.1.0.nupkg`

**Package Types:**
- `cms` - Content Management System
- `commerce` - Commerce Manager

### Package Structure

```
myapp.cms.app.1.0.0.nupkg
├── wwwroot/
│   ├── appsettings.json
│   ├── appsettings.Integration.json
│   ├── appsettings.Preproduction.json
│   ├── appsettings.Production.json
│   ├── web.config
│   ├── bin/
│   ├── modules/
│   └── [other web app files]
├── dxpPlatformSettings.json (optional)
└── [package metadata]
```

### Platform Settings (Optional)

**dxpPlatformSettings.json:**

```json
{
  "$schema": "https://schema.episerver.net/paasportal/2022-03-24/platformschema.json",
  "entrypoint": "MyApp.dll",
  "platformPackages": [
    {
      "name": "NodeJs",
      "version": 18
    }
  ]
}
```

---

## Important Limitations

1. **Cannot include BLOB and DB packages** while deploying through code packages
2. **Cannot deploy from Integration to Production** directly
3. **Cannot complete/reset Integration deployments** via portal (API only)
4. **Cannot show custom maintenance page** for content-only deployments
5. **One deployment at a time** per DXP project
6. **Production database overwrite** disabled after go-live
7. **Direct Deploy** only available for Integration environment

---

## Deployment Workflow

### Standard Deployment (with Slot)

1. **Start Deployment** → Status: `InProgress`
2. **Wait for Completion** → Status: `AwaitingVerification`
3. **Validate Slot** (manual or automated testing)
4. **Complete** or **Reset** deployment
5. If completed → Status: `Succeeded`
6. If reset → Status: `Redeployed`

### Direct Deploy (Integration Only)

1. **Start Deployment** with `directDeploy: true`
2. **Deployment completes automatically** → Status: `Succeeded`
3. No verification step or slot swap required

---

## Environment-Specific Configuration

Config transformations are automatically applied based on target environment:

- `web.Integration.config`
- `web.Preproduction.config`
- `web.Production.config`

Or for appsettings:

- `appsettings.Integration.json`
- `appsettings.Preproduction.json`
- `appsettings.Production.json`

---

## Rate Limits

- API rate limits are enforced per project
- Check response headers for rate limit status
- Use caching where possible to minimize API calls

---

## Error Responses

### Common HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Invalid or missing authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `409 Conflict` - Deployment already in progress
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": {
    "code": "DeploymentInProgress",
    "message": "A deployment is already in progress for this project",
    "details": []
  }
}
```

---

## PowerShell Module

The official **EpiCloud** PowerShell module wraps the API:

```powershell
Install-Module EpiCloud -Scope CurrentUser

# Connect
Connect-EpiCloud -ClientKey $key -ClientSecret $secret -ProjectId $projectId

# Start deployment
Start-EpiDeployment -DeploymentPackage "cms.app.1.0.0.nupkg" `
                    -TargetEnvironment Integration `
                    -DirectDeploy

# Get status
Get-EpiDeployment -Id $deploymentId

# Complete deployment
Complete-EpiDeployment -Id $deploymentId -Wait

# Reset deployment
Reset-EpiDeployment -Id $deploymentId
```

---

## Best Practices

1. **Always use HTTPS** for API requests
2. **Store secrets securely** - never commit ClientSecret to source control
3. **Implement retry logic** with exponential backoff
4. **Monitor deployment status** regularly using polling
5. **Use DirectDeploy** for Integration to speed up CI/CD
6. **Test in Integration first** before promoting to Preproduction/Production
7. **Validate slots thoroughly** before completing deployments
8. **Use maintenance page** for breaking changes to database schema
9. **Keep package names clean** - no spaces or special characters
10. **Set appropriate timeouts** - deployments can take 5-30+ minutes

---

## Additional Resources

- **Official Documentation:** https://docs.developers.optimizely.com/digital-experience-platform/docs/deployment-api
- **PowerShell Gallery:** https://www.powershellgallery.com/packages/EpiCloud
- **DXP Management Portal:** https://paasportal.episerver.net
- **Community Extensions:** 
  - [Epinova Azure DevOps Extension](https://github.com/Epinova/epinova-dxp-deployment)
  - [Luminos GitHub Actions](https://github.com/marketplace/actions/deploy-to-optimizely-dxp)

---

## Support

For API issues or questions:
- **Optimizely Support:** https://support.optimizely.com
- **Developer Community:** https://world.optimizely.com

---

**Document Version:** 1.0  
**Last Updated:** October 10, 2025  
**Compiled from:** Official Optimizely documentation, PowerShell module behavior, and community implementations