/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, ReactNode, FormEvent } from 'react';
import { 
  ArrowLeft, 
  Info, 
  Search, 
  ChevronDown, 
  Bookmark, 
  Home, 
  BookOpen, 
  Timer, 
  User 
} from 'lucide-react';
import { motion } from 'motion/react';

interface Exercise {
  id: string;
  name: string;
  description: string;
  difficulty: 'Principiante' | 'Intermedio' | 'Avanzado';
  image: string;
  tags: string[];
  duration: string;
  isBookmarked: boolean;
}

const EXERCISES: Exercise[] = [
  {
    id: '1',
    name: 'Venus',
    description: 'Postura fundamental de pie para la apertura inicial de la caja torácica y alineación.',
    difficulty: 'Principiante',
    image: 'https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?auto=format&fit=crop&q=80&w=800',
    tags: ['Enfoque en Diafragma'],
    duration: '5-10 min',
    isBookmarked: true,
  },
  {
    id: '2',
    name: 'Maya',
    description: 'Posición de rodillas centrada en la estabilidad del core y activación profunda del suelo pélvico.',
    difficulty: 'Intermedio',
    image: 'https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&q=80&w=800',
    tags: ['Suelo Pélvico'],
    duration: '12 min',
    isBookmarked: false,
  },
  {
    id: '3',
    name: 'Hestia',
    description: 'Postura sentada que requiere un alto control del transverso abdominal y el serrato anterior.',
    difficulty: 'Avanzado',
    image: 'https://images.unsplash.com/photo-1599447421416-3414500d18a5?auto=format&fit=crop&q=80&w=800',
    tags: ['Serrato/Core'],
    duration: '15 min',
    isBookmarked: false,
  },
];

const CATEGORIES = ['Todas las posturas', 'De pie', 'De rodillas', 'Supino'];

type Tab = 'Inicio' | 'Biblioteca' | 'Ejercicios' | 'Perfil';

interface UserProfile {
  name: string;
  height: string;
  weight: string;
  age: string;
}

export default function App() {
  const [activeTab, setActiveTab] = useState<Tab>('Biblioteca');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeCategory, setActiveCategory] = useState('Todas las posturas');
  const [isRegistered, setIsRegistered] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile>({
    name: '',
    height: '',
    weight: '',
    age: '',
  });

  const filteredExercises = EXERCISES.filter((exercise) => {
    const query = searchQuery.toLowerCase();
    return (
      exercise.name.toLowerCase().includes(query) ||
      exercise.description.toLowerCase().includes(query) ||
      exercise.tags.some((tag) => tag.toLowerCase().includes(query))
    );
  });

  const handleRegister = (e: FormEvent) => {
    e.preventDefault();
    if (userProfile.name && userProfile.height && userProfile.weight && userProfile.age) {
      setIsRegistered(true);
      setActiveTab('Inicio');
    }
  };

  if (!isRegistered) {
    return (
      <div className="min-h-screen bg-[#0a0f16] text-slate-100 font-sans p-6 flex flex-col justify-center">
        <motion.div 
          initial={{ opacity: 0, y: 20 }} 
          animate={{ opacity: 1, y: 0 }}
          className="max-w-md mx-auto w-full"
        >
          <div className="text-center mb-10">
            <div className="w-20 h-20 bg-blue-600 rounded-3xl flex items-center justify-center mb-6 mx-auto shadow-xl shadow-blue-600/20 rotate-3">
              <User className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold mb-2">Bienvenido a TRH</h1>
            <p className="text-slate-400">Crea tu perfil para personalizar tu experiencia de entrenamiento.</p>
          </div>

          <form onSubmit={handleRegister} className="space-y-5">
            <div>
              <label className="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Nombre Completo</label>
              <input
                type="text"
                required
                placeholder="Ej. Ana García"
                className="w-full bg-slate-900 border border-slate-800 rounded-2xl py-4 px-5 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                value={userProfile.name}
                onChange={(e) => setUserProfile({ ...userProfile, name: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Talla (cm)</label>
                <input
                  type="number"
                  required
                  placeholder="170"
                  className="w-full bg-slate-900 border border-slate-800 rounded-2xl py-4 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  value={userProfile.height}
                  onChange={(e) => setUserProfile({ ...userProfile, height: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Peso (kg)</label>
                <input
                  type="number"
                  required
                  placeholder="65"
                  className="w-full bg-slate-900 border border-slate-800 rounded-2xl py-4 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  value={userProfile.weight}
                  onChange={(e) => setUserProfile({ ...userProfile, weight: e.target.value })}
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Edad</label>
                <input
                  type="number"
                  required
                  placeholder="28"
                  className="w-full bg-slate-900 border border-slate-800 rounded-2xl py-4 px-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 transition-all"
                  value={userProfile.age}
                  onChange={(e) => setUserProfile({ ...userProfile, age: e.target.value })}
                />
              </div>
            </div>

            <button
              type="submit"
              className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-2xl mt-8 shadow-lg shadow-blue-600/20 transition-all transform active:scale-[0.98]"
            >
              Comenzar ahora
            </button>
          </form>
        </motion.div>
      </div>
    );
  }

  const renderContent = () => {
    switch (activeTab) {
      case 'Inicio':
        return (
          <div className="px-4 py-10 flex flex-col items-center justify-center text-center">
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}>
              <div className="w-20 h-20 bg-blue-600/20 rounded-full flex items-center justify-center mb-6 mx-auto">
                <Home className="w-10 h-10 text-blue-500" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Bienvenido, {userProfile.name.split(' ')[0]}</h2>
              <p className="text-slate-400 max-w-xs mx-auto">
                Tu compañero diario para ejercicios hipopresivos y bienestar postural.
              </p>
              <div className="mt-10 grid gap-4 w-full">
                <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 text-left">
                  <p className="text-xs font-bold text-blue-500 uppercase mb-1">Tu progreso</p>
                  <p className="text-lg font-bold">3 sesiones esta semana</p>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 text-left">
                  <p className="text-xs font-bold text-emerald-500 uppercase mb-1">Próximo objetivo</p>
                  <p className="text-lg font-bold">Completar nivel Principiante</p>
                </div>
              </div>
            </motion.div>
          </div>
        );
      case 'Biblioteca':
        return (
          <>
            {/* Search Bar */}
            <div className="px-4 py-4">
              <div className="relative group">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  <Search className="w-5 h-5 text-slate-500 group-focus-within:text-blue-400 transition-colors" />
                </div>
                <input
                  type="text"
                  placeholder="Buscar posturas (ej. Venus)"
                  className="w-full bg-slate-900/50 border border-slate-800 rounded-xl py-3 pl-11 pr-4 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all placeholder:text-slate-500"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
            </div>

            {/* Categories */}
            <div className="flex gap-3 px-4 pb-6 overflow-x-auto no-scrollbar">
              {CATEGORIES.map((category) => (
                <button
                  key={category}
                  onClick={() => setActiveCategory(category)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all whitespace-nowrap border ${
                    activeCategory === category
                      ? 'bg-blue-600 border-blue-500 text-white shadow-lg shadow-blue-600/20'
                      : 'bg-slate-900/50 border-slate-800 text-slate-400 hover:border-slate-700'
                  }`}
                >
                  {category}
                  {category !== 'Todas las posturas' && <ChevronDown className="w-4 h-4 opacity-50" />}
                </button>
              ))}
            </div>

            {/* Exercise List */}
            <div className="px-4 space-y-6">
              <div className="flex items-center justify-between px-1">
                <h2 className="text-lg font-bold tracking-tight">
                  {searchQuery ? 'Resultados de búsqueda' : 'Posturas recomendadas'}
                </h2>
                {searchQuery && (
                  <span className="text-xs text-slate-500 font-medium">
                    {filteredExercises.length} {filteredExercises.length === 1 ? 'resultado' : 'resultados'}
                  </span>
                )}
              </div>
              
              <div className="grid gap-6">
                {filteredExercises.length > 0 ? (
                  filteredExercises.map((exercise, index) => (
                    <motion.div
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 }}
                      key={exercise.id}
                      className="group relative bg-slate-900/30 border border-slate-800/50 rounded-2xl overflow-hidden hover:border-blue-500/30 transition-all cursor-pointer"
                    >
                      {/* Image Container */}
                      <div className="relative aspect-[16/9] overflow-hidden">
                        <img
                          src={exercise.image}
                          alt={exercise.name}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                          referrerPolicy="no-referrer"
                        />
                        <div className="absolute top-3 right-3">
                          <span className={`px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider text-white backdrop-blur-md ${
                            exercise.difficulty === 'Principiante' ? 'bg-emerald-500/80' :
                            exercise.difficulty === 'Intermedio' ? 'bg-amber-500/80' : 'bg-rose-500/80'
                          }`}>
                            {exercise.difficulty}
                          </span>
                        </div>
                      </div>

                      {/* Content */}
                      <div className="p-5">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-xl font-bold">{exercise.name}</h3>
                          <Bookmark 
                            className={`w-5 h-5 transition-colors ${
                              exercise.isBookmarked ? 'text-blue-500 fill-blue-500' : 'text-slate-500'
                            }`} 
                          />
                        </div>
                        <p className="text-sm text-slate-400 leading-relaxed mb-4">
                          {exercise.description}
                        </p>
                        <div className="flex flex-wrap gap-2">
                          {exercise.isBookmarked && (
                            <span className="px-3 py-1 bg-amber-500/10 text-amber-500 text-xs font-semibold rounded-lg border border-amber-500/20 flex items-center gap-1">
                              <Bookmark className="w-3 h-3 fill-amber-500" />
                              Favorito
                            </span>
                          )}
                          {exercise.tags.map(tag => (
                            <span key={tag} className="px-3 py-1 bg-blue-500/10 text-blue-400 text-xs font-semibold rounded-lg border border-blue-500/20">
                              {tag}
                            </span>
                          ))}
                          <span className="px-3 py-1 bg-slate-800/50 text-slate-400 text-xs font-semibold rounded-lg border border-slate-700/50">
                            {exercise.duration}
                          </span>
                        </div>
                      </div>
                    </motion.div>
                  ))
                ) : (
                  <motion.div 
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="flex flex-col items-center justify-center py-20 text-center"
                  >
                    <div className="w-16 h-16 bg-slate-900 rounded-full flex items-center justify-center mb-4">
                      <Search className="w-8 h-8 text-slate-700" />
                    </div>
                    <h3 className="text-lg font-bold mb-1">No se encontraron resultados</h3>
                    <p className="text-sm text-slate-500 max-w-[240px]">
                      No pudimos encontrar nada que coincida con "{searchQuery}". Intenta con otros términos.
                    </p>
                    <button 
                      onClick={() => setSearchQuery('')}
                      className="mt-6 text-blue-500 text-sm font-bold hover:text-blue-400 transition-colors"
                    >
                      Limpiar búsqueda
                    </button>
                  </motion.div>
                )}
              </div>
            </div>
          </>
        );
      case 'Ejercicios':
        return (
          <div className="px-4 py-10 text-center">
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
              <div className="w-20 h-20 bg-amber-600/20 rounded-full flex items-center justify-center mb-6 mx-auto">
                <Timer className="w-10 h-10 text-amber-500" />
              </div>
              <h2 className="text-2xl font-bold mb-2">Tus Rutinas</h2>
              <p className="text-slate-400 mb-8">Aquí aparecerán tus rutinas personalizadas y entrenamientos activos.</p>
              <button className="w-full bg-blue-600 py-4 rounded-2xl font-bold shadow-lg shadow-blue-600/20">
                Empezar nueva rutina
              </button>
            </motion.div>
          </div>
        );
      case 'Perfil':
        return (
          <div className="px-4 py-10">
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div className="flex items-center gap-4 mb-10">
                <div className="w-16 h-16 bg-blue-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-600/20">
                  <User className="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-bold">{userProfile.name || 'Usuario TRH'}</h2>
                  <p className="text-sm text-slate-500">Miembro desde Feb 2024</p>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4 mb-10">
                <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 text-center">
                  <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Talla</p>
                  <p className="text-lg font-bold">{userProfile.height} <span className="text-xs font-normal text-slate-500">cm</span></p>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 text-center">
                  <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Peso</p>
                  <p className="text-lg font-bold">{userProfile.weight} <span className="text-xs font-normal text-slate-500">kg</span></p>
                </div>
                <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 text-center">
                  <p className="text-[10px] font-bold text-slate-500 uppercase mb-1">Edad</p>
                  <p className="text-lg font-bold">{userProfile.age} <span className="text-xs font-normal text-slate-500">años</span></p>
                </div>
              </div>

              <div className="space-y-4">
                <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 flex items-center justify-between group cursor-pointer hover:border-slate-700 transition-colors">
                  <span className="font-medium">Configuración de cuenta</span>
                  <ChevronDown className="w-5 h-5 -rotate-90 text-slate-600" />
                </div>
                <div className="bg-slate-900/50 p-4 rounded-2xl border border-slate-800 flex items-center justify-between group cursor-pointer hover:border-slate-700 transition-colors">
                  <span className="font-medium">Notificaciones</span>
                  <ChevronDown className="w-5 h-5 -rotate-90 text-slate-600" />
                </div>
                <button 
                  onClick={() => setIsRegistered(false)}
                  className="w-full bg-rose-500/10 text-rose-500 p-4 rounded-2xl border border-rose-500/20 font-bold hover:bg-rose-500/20 transition-all mt-10"
                >
                  Cerrar sesión / Nuevo Usuario
                </button>
              </div>
            </motion.div>
          </div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0f16] text-slate-100 font-sans selection:bg-blue-500/30">
      {/* Header */}
      <header className="sticky top-0 z-20 flex items-center bg-[#0a0f16]/80 backdrop-blur-md px-4 py-3 border-b border-slate-800/50">
        <button className="p-2 hover:bg-slate-800 rounded-full transition-colors">
          <ArrowLeft className="w-6 h-6" />
        </button>
        <h1 className="flex-1 text-center text-lg font-bold tracking-tight">
          {activeTab === 'Biblioteca' ? 'Biblioteca de Ejercicios TRH' : activeTab}
        </h1>
        <button className="p-2 hover:bg-slate-800 rounded-full transition-colors">
          <Info className="w-6 h-6" />
        </button>
      </header>

      <main className="pb-24 max-w-2xl mx-auto">
        {renderContent()}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-30 bg-[#0a0f16]/95 backdrop-blur-lg border-t border-slate-800/50 px-6 pt-3 pb-8 flex items-center justify-between max-w-2xl mx-auto">
        <NavItem 
          icon={<Home className="w-6 h-6" />} 
          label="Inicio" 
          active={activeTab === 'Inicio'} 
          onClick={() => setActiveTab('Inicio')}
        />
        <NavItem 
          icon={<BookOpen className="w-6 h-6" />} 
          label="Biblioteca" 
          active={activeTab === 'Biblioteca'} 
          onClick={() => setActiveTab('Biblioteca')}
        />
        <NavItem 
          icon={<Timer className="w-6 h-6" />} 
          label="Ejercicios" 
          active={activeTab === 'Ejercicios'} 
          onClick={() => setActiveTab('Ejercicios')}
        />
        <NavItem 
          icon={<User className="w-6 h-6" />} 
          label="Perfil" 
          active={activeTab === 'Perfil'} 
          onClick={() => setActiveTab('Perfil')}
        />
      </nav>
    </div>
  );
}

function NavItem({ icon, label, active = false, onClick }: { icon: ReactNode, label: string, active?: boolean, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      className={`flex flex-col items-center gap-1 transition-colors ${active ? 'text-blue-500' : 'text-slate-500 hover:text-slate-300'}`}
    >
      <div className={active ? 'scale-110 transition-transform' : ''}>
        {icon}
      </div>
      <span className="text-[10px] font-bold uppercase tracking-wider">{label}</span>
    </button>
  );
}
