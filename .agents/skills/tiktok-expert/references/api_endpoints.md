# TikTok Endpoints & Data Structures Catalog

## 1. SSR Extraction: `__UNIVERSAL_DATA_FOR_REHYDRATION__`

The most efficient and stealthy method for extracting TikTok data is requesting the target video or profile URL and parsing the script tag:
```html
<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">
```

### Key JSON Navigation Paths:

#### For Videos (`https://www.tiktok.com/@user/video/ID`):
```text
data["__DEFAULT_SCOPE__"]["webapp.video-detail"]["itemInfo"]["itemStruct"]
```
Available properties in `itemStruct`:
- `id`: Unique video ID.
- `desc`: Video description text (captions and hashtags).
- `createTime`: Unix timestamp of creation.
- `video`:
  - `playAddr`: Direct CDN stream URL (clean / watermark-free).
  - `downloadAddr`: Direct download URL.
  - `duration`: Video duration in seconds.
  - `ratio`: Aspect ratio resolution (e.g., `720p`, `1080p`).
  - `bitrate`: Stream bitrate.
- `author`:
  - `id`, `uniqueId` (user handle), `nickname`, `avatarLarger`, `verified`, `secUid`.
- `music`:
  - `id`, `title`, `authorName`, `playUrl`, `duration`.
- `stats`:
  - `diggCount` (likes), `shareCount`, `commentCount`, `playCount`, `collectCount` (bookmarks).

#### For User Profiles (`https://www.tiktok.com/@user`):
```text
data["__DEFAULT_SCOPE__"]["webapp.user-detail"]["userInfo"]
```
Available properties:
- `user`: Account info, bio (`signature`), external links, verification badges.
- `stats`: `followerCount`, `followingCount`, `heartCount` (lifetime likes), `videoCount`.

---

## 2. TikTok Internal Web API Endpoints

### Endpoint 1: User Video Feed
- **URL:** `https://www.tiktok.com/api/post/item_list/`
- **Method:** `GET`
- **Primary Query Parameters:**
  - `secUid`: User's cryptographic ID (found on user profile).
  - `count`: Batch size (default `30`).
  - `cursor`: Pagination cursor (`0` for initial page).
  - `msToken`, `X-Bogus`: Dynamic request signatures.
- **Required Cookies:** `ttwid`.

### Endpoint 2: Video Comments
- **URL:** `https://www.tiktok.com/api/comment/list/`
- **Method:** `GET`
- **Primary Query Parameters:**
  - `aweme_id`: Target video ID.
  - `cursor`: Pagination offset (`0` for first page).
  - `count`: Number of comments per page (typically `20` or `50`).
  - `msToken`, `X-Bogus`: Dynamic request signatures.
- **Required Cookies:** `ttwid`.

### Endpoint 3: Content Search
- **URL:** `https://www.tiktok.com/api/search/item/full/`
- **Method:** `GET`
- **Primary Query Parameters:**
  - `keyword`: Search query string.
  - `offset`: Pagination offset (`0`, `20`, `40`...).
  - `search_source`: Query origin (e.g., `search_box`).
