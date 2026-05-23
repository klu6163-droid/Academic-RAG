import { useState } from 'react';
import type { ProjectSynthesis } from '../types';
import { ChevronDown, ChevronRight } from 'lucide-react';

export function ProjectViews({ projects }: { projects: ProjectSynthesis[] }) {
  const [open, setOpen] = useState<Set<number>>(new Set([0]));

  const toggle = (i: number) => {
    setOpen(prev => {
      const next = new Set(prev);
      next.has(i) ? next.delete(i) : next.add(i);
      return next;
    });
  };

  return (
    <div>
      <h2 className="text-2xl font-bold mb-4">Project Syntheses</h2>
      <p className="text-sm text-gray-500 mb-6">{projects.length} project-specific literature syntheses</p>

      <div className="space-y-4">
        {projects.map((proj, i) => {
          const isOpen = open.has(i);
          return (
            <div key={i} className="bg-white rounded-lg shadow">
              <button onClick={() => toggle(i)} className="w-full text-left px-5 py-4 flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-gray-800">{proj.title}</h3>
                  <p className="text-sm text-gray-500 mt-0.5">{proj.file}</p>
                </div>
                {isOpen ? <ChevronDown size={18} className="text-gray-400" /> : <ChevronRight size={18} className="text-gray-400" />}
              </button>
              {isOpen && (
                <div className="px-5 pb-5 border-t">
                  {proj.sections.map((sec, j) => (
                    <div key={j} className="mt-4">
                      <h4 className="text-sm font-medium text-gray-700 mb-2">{sec.heading}</h4>
                      <div className="text-sm text-gray-600 whitespace-pre-wrap leading-relaxed bg-gray-50 rounded p-3">{sec.content}</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
