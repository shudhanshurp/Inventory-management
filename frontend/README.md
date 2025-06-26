# Next.js Frontend for AI Order Processor

This is the frontend for the AI-powered order processing and analytics system. It is built with Next.js, React, and Tailwind CSS, and provides a modern dashboard for business analytics, order management, and inventory insights.

## Features

- **Analysis Dashboard**: Visualize sales trends, forecasts, product performance, inventory health, and catalog suggestions.
- **Order Management**: Paginated order history with detailed modal views and PDF export.
- **Inventory Management**: Paginated inventory table with stock status indicators.
- **Responsive UI**: Built with Tailwind CSS for a clean, adaptive experience.
- **Swiper Carousels**: Used for low/out-of-stock and inventory forecast carousels.
- **Nivo Charts**: Interactive line and bar charts for analytics.

## Getting Started

First, install dependencies:

```bash
npm install
# or
yarn install
```

Then, run the development server:

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the dashboard.

## Key Pages

- `/dashboard` — Main analytics dashboard (sales, inventory, product performance, forecasts)
- `/orders` — Paginated order history with detail modals and PDF export
- `/inventory` — Paginated inventory table with stock status
- `/email-processor` — Submit email orders for processing

## Dependencies

- **Next.js** (v15+)
- **React** (v19+)
- **Tailwind CSS**
- **Swiper** (for carousels)
- **@nivo/line** and **@nivo/bar** (for charts)
- **lucide-react** (icons)

## Swiper Usage

Swiper is used for carousels in the dashboard (inventory insights, future inventory needs). Navigation arrows are styled via global CSS.

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Swiper Documentation](https://swiperjs.com/react)
- [Nivo Documentation](https://nivo.rocks/line/)

## Deployment

Deploy easily on [Vercel](https://vercel.com/) or your preferred platform.
