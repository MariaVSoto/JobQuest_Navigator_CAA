import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

export async function extractSkillsWithSpacy(resume: string): Promise<string[]> {
  return new Promise((resolve, reject) => {
    const scriptPath = path.join(__dirname, '../extract_skills.py');
    const py = spawn('python', [scriptPath]);
    let data = '';
    let error = '';

    py.stdout.on('data', (chunk) => (data += chunk));
    py.stderr.on('data', (chunk) => (error += chunk));
    py.on('close', (code) => {
      if (code !== 0) return reject(error);
      try {
        const skills = JSON.parse(data);
        resolve(skills);
      } catch (e) {
        reject(e);
      }
    });

    py.stdin.write(resume);
    py.stdin.end();
  });
}

export function mapSkillsToCertifications(skills: string[]): Record<string, any> {
  const certPath = path.join(__dirname, '../certificationMap.json');
  const certData = JSON.parse(fs.readFileSync(certPath, 'utf-8'));
  const result: Record<string, any> = {};
  for (const skill of skills) {
    const key = skill.toLowerCase();
    if (certData[key]) {
      result[skill] = certData[key];
    }
  }
  return result;
} 