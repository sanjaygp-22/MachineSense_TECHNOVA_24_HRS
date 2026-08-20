# Frontend Render Error Analysis (`FRONTEND_RENDER_ERROR.md`)

## 1. Exact Error
`Uncaught ReferenceError: totalMachines is not defined` (followed by `ReferenceError: healthyCount is not defined`, `ReferenceError: alertCount is not defined`, and `ReferenceError: TrendChart is not defined`).

## 2. File Causing the Error
`frontend/src/pages/Dashboard.jsx` (Link: [Dashboard.jsx](file:///d:/projects/MachineSense2/frontend/src/pages/Dashboard.jsx#L52))

## 3. Lines Causing the Error
- **Line 52**: `{totalMachines}`
- **Line 55**: `{healthyCount}`
- **Line 69**: `{alertCount}`
- **Line 207**: `<TrendChart height={180} />` (without `TrendChart` import at top of file)

## 4. Why It Happens
During a recent refactoring chunk edit on `Dashboard.jsx`, the calculation variables (`totalMachines`, `healthyCount`, `alertCount`) and the `import TrendChart from '../components/charts/TrendChart'` statement were stripped from the top of `Dashboard.jsx`. When React attempted to mount `<Dashboard />`, JavaScript threw uncaught `ReferenceError` runtime exceptions, causing React's render phase to crash completely before any DOM nodes could be rendered, resulting in a blank screen.

## 5. Minimal Frontend-Only Fix
1. Add `import TrendChart from '../components/charts/TrendChart';` to `Dashboard.jsx`.
2. Compute `totalMachines`, `healthyCount`, and `alertCount` from `machinesData` inside `Dashboard()` component function:
```jsx
const totalMachines = machinesData.length;
const healthyCount = machinesData.filter((m) => m.status === 'Healthy' || m.status === 'Normal').length;
const alertCount = machinesData.filter((m) => m.status !== 'Healthy' && m.status !== 'Normal').length;
```
