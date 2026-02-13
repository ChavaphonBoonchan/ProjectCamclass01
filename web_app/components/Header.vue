<template>
  <header class="bg-gradient-to-r from-blue-50 to-white shadow-md sticky top-0 z-50 border-b-2 border-blue-200">
    <div class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Logo and Title -->
        <div class="flex items-center">
          <div class="flex items-center">
            <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center mr-3">
              <Camera size="20" class="text-white" />
            </div>
            <h1 class="text-xl font-bold bg-gradient-to-r from-blue-600 to-blue-400 bg-clip-text text-transparent">Cam-Class01</h1>
          </div>
        </div>
        
        <!-- Navigation -->
        <nav class="hidden md:flex space-x-6">
          <NuxtLink 
            to="/" 
            class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-100 rounded-lg': $route.path === '/' }">
            <div class="flex items-center">
              <ClipboardCheck size="16" class="mr-1" />
              เช็คชื่อ
            </div>
          </NuxtLink>
          
          <NuxtLink 
            to="/dashboard" 
            class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-100 rounded-lg': $route.path === '/dashboard' }">
            <div class="flex items-center">
              <LayoutDashboard size="16" class="mr-1" />
              สถิติการมาเรียน
            </div>
          </NuxtLink>
          
          
          <NuxtLink 
            to="/history" 
            class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-100 rounded-lg': $route.path === '/history' }">
            <div class="flex items-center">
              <FileEdit size="16" class="mr-1" />
              แก้ไขประวัติ
            </div>
          </NuxtLink>
          
          <NuxtLink 
            to="/students" 
            class="text-gray-700 hover:text-blue-600 px-3 py-2 text-sm font-medium transition-colors"
            :class="{ 'text-blue-600 bg-blue-100 rounded-lg': $route.path === '/students' }">
            <div class="flex items-center">
              <Users size="16" class="mr-1" />
              นักเรียน
            </div>
          </NuxtLink>
        </nav>
        
        <!-- Status Indicator -->
        <div class="flex items-center space-x-4">
          <div class="flex items-center">
            <div class="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></div>
            <span class="text-sm text-gray-600">กำลังเชื่อมต่อ AI CAM</span>
          </div>
          
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { Camera, Users, LayoutDashboard, ClipboardCheck, FileEdit } from 'lucide-vue-next'

// State
const lastUpdate = ref('')

// Update time every second (only on client)
onMounted(() => {
  lastUpdate.value = new Date().toLocaleTimeString()
  setInterval(() => {
    lastUpdate.value = new Date().toLocaleTimeString()
  }, 1000)
})
</script>
