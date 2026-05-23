/// <reference types="vite/client" />

declare module 'react-force-graph-2d' {
  import { Component } from 'react';

  interface ForceGraphProps {
    graphData: { nodes: any[]; links: any[] };
    width?: number;
    height?: number;
    nodeCanvasObject?: (node: any, ctx: CanvasRenderingContext2D, globalScale?: number) => void;
    nodePointerAreaPaint?: (node: any, color: string, ctx: CanvasRenderingContext2D) => void;
    onNodeClick?: (node: any) => void;
    linkColor?: (link: any) => string;
    linkWidth?: (link: any) => number;
    linkDirectionalArrowLength?: number;
    linkDirectionalArrowRelPos?: number;
    cooldownTicks?: number;
    [key: string]: any;
  }

  export default class ForceGraph2D extends Component<ForceGraphProps> {}
}
