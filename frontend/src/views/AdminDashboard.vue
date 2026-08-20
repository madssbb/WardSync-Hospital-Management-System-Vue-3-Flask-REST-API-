<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const stats = ref({ doctors: 0, patients: 0, appointments: 0 })
const currentView = ref('stats')
const doctors = ref([])
const patients = ref([])
const specs = ref([])
const appointments = ref([])
const searchQ = ref('')
const searchSpec = ref('')
const appointmentStatusFilter = ref('All')
const appointmentSearch = ref('')
const newDoc = ref({ name: '', username: '', email: '', password: '', specialization_id: null, experience: 0 })
const editDoc = ref(null)
const editPatientData = ref(null)
const patientHistory = ref(null)
const newSpec = ref({ name: '', description: '' })
const statusMsg = ref({ text: '', type: '' })

const fetchDoctors = async () => {
    const res = await axios.get('/api/admin/doctors', { params: { q: searchQ.value, specialization_id: searchSpec.value || undefined } })
    doctors.value = res.data
}

const fetchPatients = async () => {
    const res = await axios.get('/api/admin/patients', { params: { q: searchQ.value } })
    patients.value = res.data
}

const fetchSpecs = async () => {
    const res = await axios.get('/api/admin/specializations')
    specs.value = res.data
}

const fetchAppointments = async () => {
    const res = await axios.get('/api/admin/appointments', {
        params: { status: appointmentStatusFilter.value === 'All' ? undefined : appointmentStatusFilter.value, q: appointmentSearch.value || undefined }
    })
    appointments.value = res.data
}

const blacklistDoctor = async (id) => {
    if (confirm('Are you sure you want to remove this doctor?')) {
        try {
            await axios.delete(`/api/admin/doctors/${id}`)
            await fetchDoctors()
            showMsg('Doctor removed successfully')
        } catch (err) {
            showMsg('Failed to remove doctor', 'danger')
        }
    }
}

const toggleActivateDoctor = async (id) => {
    try {
        // Reuse the same toggle endpoint used for patients
        const doctor = doctors.value.find(d => d.id === id)
        if (!doctor) return
        // Find the user for this doctor — backend delete toggles is_active
        // We re-activate by calling DELETE which flips is_active to false already
        // Instead, use a direct re-enable via the patient toggle pattern
        await axios.post(`/api/admin/doctors/${id}/restore`)
        await fetchDoctors()
        showMsg('Doctor restored successfully')
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Failed to restore doctor', 'danger')
    }
}

const togglePatient = async (id) => {
    await axios.post(`/api/admin/patients/${id}/toggle-active`)
    fetchPatients()
}

const fetchPatientHistory = async (id) => {
    try {
        const res = await axios.get(`/api/admin/patients/${id}/history`)
        patientHistory.value = res.data
    } catch (err) {
        showMsg('Failed to fetch patient history', 'danger')
    }
}

const openEditPatient = (patient) => {
    editPatientData.value = {
        id: patient.id,
        name: patient.name,
        contact: patient.contact || '',
        dob: patient.dob || '',
        email: patient.email
    }
}

const updatePatient = async () => {
    try {
        await axios.put(`/api/admin/patients/${editPatientData.value.id}`, editPatientData.value)
        await fetchPatients()
        showMsg('Patient updated successfully')
        editPatientData.value = null
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Failed to update patient', 'danger')
    }
}

const showMsg = (text, type = 'success') => {
    statusMsg.value = { text, type }
    setTimeout(() => { statusMsg.value = { text: '', type: '' } }, 3000)
}

const addDoctor = async () => {
    try {
        await axios.post('/api/admin/doctors', newDoc.value)
        newDoc.value = { name: '', username: '', email: '', password: '', specialization_id: null, experience: 0 }
        await fetchDoctors()
        showMsg('Doctor added successfully')
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Failed to add doctor', 'danger')
    }
}

const openEditModal = (doc) => {
    const spec = specs.value.find(s => s.name === doc.specialization)
    editDoc.value = { 
        id: doc.id, 
        name: doc.name, 
        specialization_id: spec ? spec.id : null, 
        experience: doc.experience 
    }
}

const updateDoctor = async () => {
    try {
        await axios.put(`/api/admin/doctors/${editDoc.value.id}`, editDoc.value)
        await fetchDoctors()
        showMsg('Doctor updated successfully')
        editDoc.value = null
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Failed to update doctor', 'danger')
    }
}

const addSpec = async () => {
    try {
        await axios.post('/api/admin/specializations', newSpec.value)
        newSpec.value = { name: '', description: '' }
        await fetchSpecs()
        showMsg('Specialization added successfully')
    } catch (err) {
        showMsg(err.response?.data?.msg || 'Failed to add specialization', 'danger')
    }
}

const statusBadgeClass = (status) => {
    if (status === 'Completed') return 'bg-success-subtle text-success'
    if (status === 'Cancelled') return 'bg-danger-subtle text-danger'
    return 'bg-primary-subtle text-primary'
}

onMounted(async () => {
    try {
        const response = await axios.get('/api/admin/stats')
        stats.value = response.data
    } catch (err) {
        console.error('Failed to fetch stats', err)
    }
    fetchSpecs()
})

const setView = (view) => {
    currentView.value = view
    searchQ.value = ''
    searchSpec.value = ''
    if (view === 'doctors') fetchDoctors()
    if (view === 'patients') fetchPatients()
    if (view === 'specs') fetchSpecs()
    if (view === 'appointments') fetchAppointments()
}
</script>

<template>
  <div class="fade-in">
    <!-- Global Status Toast-like Alert -->
    <div v-if="statusMsg.text" :class="['alert', 'alert-' + statusMsg.type, 'position-fixed', 'top-0', 'end-0', 'm-4', 'shadow-lg']" style="z-index: 9999;">
        {{ statusMsg.text }}
    </div>

    <div class="d-flex justify-content-between align-items-center mb-5">
        <div>
            <h2 class="fw-bold mb-1">Administrative Control</h2>
            <p class="text-muted mb-0">Manage providers, patients, appointments, and system specializations</p>
        </div>
        <div class="bg-white p-1 rounded-3 shadow-sm border">
            <div class="btn-group border-0">
                <button class="btn btn-sm px-3" :class="currentView === 'stats' ? 'btn-primary shadow-sm' : 'btn-light'" @click="setView('stats')">Analytics</button>
                <button class="btn btn-sm px-3" :class="currentView === 'doctors' ? 'btn-primary shadow-sm' : 'btn-light'" @click="setView('doctors')">Doctors</button>
                <button class="btn btn-sm px-3" :class="currentView === 'patients' ? 'btn-primary shadow-sm' : 'btn-light'" @click="setView('patients')">Patients</button>
                <button class="btn btn-sm px-3" :class="currentView === 'appointments' ? 'btn-primary shadow-sm' : 'btn-light'" @click="setView('appointments')">Appointments</button>
                <button class="btn btn-sm px-3" :class="currentView === 'specs' ? 'btn-primary shadow-sm' : 'btn-light'" @click="setView('specs')">Depts</button>
            </div>
        </div>
    </div>

    <!-- Analytics View -->
    <div v-if="currentView === 'stats'" class="row g-4 mb-5">
      <div class="col-md-4">
        <div class="card border-0 p-4 h-100 overflow-hidden position-relative">
          <div class="position-absolute end-0 top-0 p-4 opacity-10">
              <i class="bi bi-person-badge" style="font-size: 5rem;"></i>
          </div>
          <h6 class="text-muted fw-bold small text-uppercase mb-2">Total Medical Staff</h6>
          <h2 class="fw-bold mb-0">{{ stats.doctors }}</h2>
          <div class="mt-3 small">
              <span class="text-success fw-bold"><i class="bi bi-arrow-up"></i> Active Doctors</span>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 p-4 h-100 overflow-hidden position-relative">
          <div class="position-absolute end-0 top-0 p-4 opacity-10">
              <i class="bi bi-people" style="font-size: 5rem;"></i>
          </div>
          <h6 class="text-muted fw-bold small text-uppercase mb-2">Registered Patients</h6>
          <h2 class="fw-bold mb-0">{{ stats.patients }}</h2>
          <div class="mt-3 small">
              <span class="text-primary fw-bold">Platform Users</span>
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card border-0 p-4 h-100 overflow-hidden position-relative">
          <div class="position-absolute end-0 top-0 p-4 opacity-10 text-info">
              <i class="bi bi-calendar-event" style="font-size: 5rem;"></i>
          </div>
          <h6 class="text-muted fw-bold small text-uppercase mb-2">Total Consultations</h6>
          <h2 class="fw-bold mb-0">{{ stats.appointments }}</h2>
          <div class="mt-3 small">
              <span class="text-info fw-bold">Life-to-date</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Doctors Management -->
    <div v-if="currentView === 'doctors'" class="card border-0 p-4 shadow-sm fade-in">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Doctor Directory</h4>
            <div class="d-flex gap-3 flex-wrap">
                <select v-model="searchSpec" class="form-select form-select-sm rounded-3 border-0 bg-light shadow-sm" style="max-width: 200px;" @change="fetchDoctors">
                    <option value="">All Specializations</option>
                    <option v-for="s in specs" :key="s.id" :value="s.id">{{ s.name }}</option>
                </select>
                <div class="input-group input-group-sm rounded-3 overflow-hidden shadow-sm" style="max-width: 220px;">
                    <span class="input-group-text bg-white border-0"><i class="bi bi-search"></i></span>
                    <input v-model="searchQ" type="text" class="form-control border-0" placeholder="Filter by name..." @input="fetchDoctors">
                </div>
                <button class="btn btn-primary btn-sm px-3 shadow-sm d-flex align-items-center gap-2" data-bs-toggle="modal" data-bs-target="#addDoctorModal">
                    <i class="bi bi-plus-lg"></i> Onboard Doctor
                </button>
            </div>
        </div>
        <div class="table-responsive">
            <table class="table hover align-middle">
                <thead>
                    <tr>
                        <th class="ps-3">Professional Info</th>
                        <th>Expertise</th>
                        <th>Exp.</th>
                        <th>Account Status</th>
                        <th class="text-end pe-3">Actions</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="doc in doctors" :key="doc.id">
                        <td class="ps-3">
                            <div class="d-flex align-items-center">
                                <div class="bg-light rounded-circle d-flex align-items-center justify-content-center me-3" style="width: 40px; height: 40px; border: 1px solid #eee;">
                                    <i class="bi bi-person-fill text-muted"></i>
                                </div>
                                <div>
                                    <span class="fw-bold d-block">{{ doc.name }}</span>
                                    <small class="text-muted">@{{ doc.username }}</small>
                                </div>
                            </div>
                        </td>
                        <td><span class="badge bg-light text-primary border border-primary-subtle px-3">{{ doc.specialization || 'General' }}</span></td>
                        <td>{{ doc.experience }} Yrs</td>
                        <td>
                            <span :class="['badge', doc.is_active ? 'bg-success-subtle text-success' : 'bg-secondary-subtle text-secondary']">
                                {{ doc.is_active ? '● Active' : '○ Blacklisted' }}
                            </span>
                        </td>
                        <td class="text-end pe-3">
                            <div class="d-flex gap-2 justify-content-end">
                                <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#editDoctorModal" @click="openEditModal(doc)">
                                    <i class="bi bi-pencil-square me-1"></i> Edit
                                </button>
                                <button class="btn btn-sm btn-outline-danger" v-if="doc.is_active" @click="blacklistDoctor(doc.id)">
                                    <i class="bi bi-slash-circle me-1"></i> Remove
                                </button>
                                <button class="btn btn-sm btn-outline-success" v-else @click="toggleActivateDoctor(doc.id)">
                                    <i class="bi bi-check-circle me-1"></i> Restore
                                </button>
                            </div>
                        </td>
                    </tr>
                    <tr v-if="doctors.length === 0">
                        <td colspan="5" class="text-center py-5 text-muted">No doctors found.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Patients Management -->
    <div v-if="currentView === 'patients'" class="card border-0 p-4 shadow-sm fade-in">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">Patient Network</h4>
            <div class="input-group input-group-sm rounded-3 overflow-hidden shadow-sm" style="max-width: 300px;">
                <span class="input-group-text bg-white border-0"><i class="bi bi-search"></i></span>
                <input v-model="searchQ" type="text" class="form-control border-0" placeholder="Search patients..." @input="fetchPatients">
            </div>
        </div>
        <div class="table-responsive">
            <table class="table hover align-middle">
                <thead>
                    <tr>
                        <th class="ps-3">Identity</th>
                        <th>Contact</th>
                        <th>Status</th>
                        <th class="text-end pe-3">Management</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="p in patients" :key="p.id">
                        <td class="ps-3">
                            <div class="d-flex align-items-center">
                                <div class="bg-info-subtle text-info rounded-3 d-flex align-items-center justify-content-center me-3" style="width: 38px; height: 38px;">
                                    <span class="fw-bold fs-6">#{{ p.id }}</span>
                                </div>
                                <span class="fw-bold">{{ p.name }}</span>
                            </div>
                        </td>
                        <td>{{ p.email }}</td>
                        <td>
                            <span :class="['badge rounded-pill', p.is_active ? 'bg-success' : 'bg-danger']">
                                {{ p.is_active ? 'Verified' : 'Suspended' }}
                            </span>
                        </td>
                        <td class="text-end pe-3">
                            <div class="d-flex gap-2 justify-content-end">
                                <button class="btn btn-sm btn-outline-primary" data-bs-toggle="modal" data-bs-target="#editPatientModal" @click="openEditPatient(p)">
                                    <i class="bi bi-pencil-square me-1"></i> Edit
                                </button>
                                <button class="btn btn-sm btn-outline-info" data-bs-toggle="modal" data-bs-target="#patientHistoryModal" @click="fetchPatientHistory(p.id)">
                                    <i class="bi bi-journal-medical me-1"></i> History
                                </button>
                                <button class="btn btn-sm" :class="p.is_active ? 'btn-outline-danger' : 'btn-success'" @click="togglePatient(p.id)">
                                    {{ p.is_active ? 'Suspend' : 'Reinstate' }}
                                </button>
                            </div>
                        </td>
                    </tr>
                    <tr v-if="patients.length === 0">
                        <td colspan="4" class="text-center py-5 text-muted">No patients found.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Appointments Management -->
    <div v-if="currentView === 'appointments'" class="card border-0 p-4 shadow-sm fade-in">
        <div class="d-flex justify-content-between align-items-center mb-4">
            <h4 class="fw-bold mb-0">All Appointments</h4>
            <div class="d-flex gap-3 flex-wrap">
                <div class="input-group input-group-sm rounded-3 overflow-hidden shadow-sm" style="max-width: 220px;">
                    <span class="input-group-text bg-white border-0"><i class="bi bi-search"></i></span>
                    <input v-model="appointmentSearch" type="text" class="form-control border-0" placeholder="Search patient..." @input="fetchAppointments">
                </div>
                <select v-model="appointmentStatusFilter" class="form-select form-select-sm rounded-3 border-0 bg-light shadow-sm" style="max-width: 160px;" @change="fetchAppointments">
                    <option value="All">All Statuses</option>
                    <option value="Booked">Booked</option>
                    <option value="Completed">Completed</option>
                    <option value="Cancelled">Cancelled</option>
                </select>
            </div>
        </div>
        <div class="table-responsive">
            <table class="table hover align-middle">
                <thead>
                    <tr>
                        <th class="ps-3">Patient</th>
                        <th>Doctor</th>
                        <th>Specialization</th>
                        <th>Date & Time</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="a in appointments" :key="a.id">
                        <td class="ps-3 fw-bold">{{ a.patient }}</td>
                        <td>Dr. {{ a.doctor }}</td>
                        <td><span class="badge bg-light text-primary border border-primary-subtle px-2">{{ a.specialization || 'General' }}</span></td>
                        <td>
                            <span class="d-block fw-semibold">{{ a.date }}</span>
                            <small class="text-muted"><i class="bi bi-clock me-1"></i>{{ a.time }}</small>
                        </td>
                        <td>
                            <span :class="['badge rounded-pill', statusBadgeClass(a.status)]">{{ a.status }}</span>
                        </td>
                    </tr>
                    <tr v-if="appointments.length === 0">
                        <td colspan="5" class="text-center py-5 text-muted">No appointments found.</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>

    <!-- Specializations -->
    <div v-if="currentView === 'specs'">
        <div class="row g-4">
            <div class="col-md-4">
                <div class="card border-0 p-4 shadow-sm">
                    <h5 class="fw-bold mb-4">Add Department</h5>
                    <form @submit.prevent="addSpec">
                        <div class="mb-3">
                            <label class="form-label small fw-semibold">Dept Name</label>
                            <input v-model="newSpec.name" type="text" class="form-control bg-light border-0" placeholder="e.g. Cardiology" required>
                        </div>
                        <div class="mb-4">
                            <label class="form-label small fw-semibold">Short Description</label>
                            <textarea v-model="newSpec.description" class="form-control bg-light border-0" rows="3" placeholder="Description..."></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 py-2 shadow-sm">Initialize Dept</button>
                    </form>
                </div>
            </div>
            <div class="col-md-8">
                <div class="card border-0 p-4 shadow-sm h-100">
                    <h5 class="fw-bold mb-4">Medical Specializations</h5>
                    <div class="row g-3">
                        <div v-for="s in specs" :key="s.id" class="col-sm-6">
                            <div class="p-3 border rounded-3 bg-light-subtle h-100">
                                <h6 class="fw-bold text-primary mb-1">{{ s.name }}</h6>
                                <p class="text-muted small mb-0">{{ s.description || 'Global department within the hospital facility.' }}</p>
                            </div>
                        </div>
                        <div v-if="specs.length === 0" class="text-center py-5">
                            <i class="bi bi-folder2-open text-muted fs-1 mb-2 d-block"></i>
                            <span class="text-muted">No departments registered yet.</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

  </div>

  <!-- Onboard Doctor Modal -->
  <div class="modal fade" id="addDoctorModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg px-2">
              <div class="modal-header border-0 pb-0">
                  <h4 class="modal-title fw-bold">Doctor Onboarding</h4>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body">
                  <form @submit.prevent="addDoctor">
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Full Name</label>
                          <input v-model="newDoc.name" type="text" class="form-control bg-light border-0" required>
                      </div>
                      <div class="row g-3 mb-3">
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">Username</label>
                              <input v-model="newDoc.username" type="text" class="form-control bg-light border-0" required>
                          </div>
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">Email</label>
                              <input v-model="newDoc.email" type="email" class="form-control bg-light border-0" required>
                          </div>
                      </div>
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Temporary Password</label>
                          <input v-model="newDoc.password" type="password" class="form-control bg-light border-0" required>
                      </div>
                      <div class="row g-3 mb-4">
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">Specialization</label>
                              <select v-model="newDoc.specialization_id" class="form-select bg-light border-0">
                                  <option v-for="s in specs" :key="s.id" :value="s.id">{{ s.name }}</option>
                              </select>
                          </div>
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">Experience (Yrs)</label>
                              <input v-model="newDoc.experience" type="number" class="form-control bg-light border-0">
                          </div>
                      </div>
                      <button type="submit" class="btn btn-primary w-100 py-2 fw-bold shadow-sm" data-bs-dismiss="modal">Register Staff Member</button>
                  </form>
              </div>
          </div>
      </div>
  </div>

  <!-- Edit Doctor Modal -->
  <div class="modal fade" id="editDoctorModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg px-2">
              <div class="modal-header border-0 pb-0">
                  <h4 class="modal-title fw-bold">Edit Doctor Portfolio</h4>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body" v-show="editDoc">
                  <form @submit.prevent="updateDoctor" v-if="editDoc">
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Full Name</label>
                          <input v-model="editDoc.name" type="text" class="form-control bg-light border-0" required>
                      </div>
                      <div class="row g-3 mb-4">
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">Specialization</label>
                              <select v-model="editDoc.specialization_id" class="form-select bg-light border-0">
                                  <option v-for="s in specs" :key="s.id" :value="s.id">{{ s.name }}</option>
                              </select>
                          </div>
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">Experience (Yrs)</label>
                              <input v-model="editDoc.experience" type="number" class="form-control bg-light border-0">
                          </div>
                      </div>
                      <button type="submit" class="btn btn-primary w-100 py-2 fw-bold shadow-sm" data-bs-dismiss="modal">Commit Updates</button>
                  </form>
              </div>
          </div>
      </div>
  </div>

  <!-- Edit Patient Modal -->
  <div class="modal fade" id="editPatientModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered">
          <div class="modal-content border-0 shadow-lg px-2">
              <div class="modal-header border-0 pb-0">
                  <h4 class="modal-title fw-bold">Update Patient Identity</h4>
                  <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body" v-if="editPatientData">
                  <form @submit.prevent="updatePatient">
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Legal Name</label>
                          <input v-model="editPatientData.name" type="text" class="form-control bg-light border-0" required>
                      </div>
                      <div class="mb-3">
                          <label class="form-label small fw-semibold">Contact Email</label>
                          <input v-model="editPatientData.email" type="email" class="form-control bg-light border-0" required>
                      </div>
                      <div class="row g-3 mb-4">
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">Phone</label>
                              <input v-model="editPatientData.contact" type="text" class="form-control bg-light border-0">
                          </div>
                          <div class="col-md-6">
                              <label class="form-label small fw-semibold">DOB</label>
                              <input v-model="editPatientData.dob" type="date" class="form-control bg-light border-0">
                          </div>
                      </div>
                      <button type="submit" class="btn btn-primary w-100 py-2 fw-bold shadow-sm" data-bs-dismiss="modal">Update Records</button>
                  </form>
              </div>
          </div>
      </div>
  </div>

  <!-- Patient History Modal (Admin View) -->
  <div class="modal fade" id="patientHistoryModal" tabindex="-1">
      <div class="modal-dialog modal-dialog-centered modal-lg">
          <div class="modal-content border-0 shadow-lg">
              <div class="modal-header bg-dark text-white border-0">
                  <div>
                    <h5 class="modal-title fw-bold">Treatment Archive: {{ patientHistory?.patient?.name }}</h5>
                    <p class="small mb-0 opacity-75">{{ patientHistory?.patient?.email }} • {{ patientHistory?.patient?.contact }}</p>
                  </div>
                  <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
              </div>
              <div class="modal-body p-4">
                  <!-- File view if exists -->
                  <div v-if="patientHistory?.patient?.file" class="alert alert-info border-0 shadow-sm mb-4 d-flex justify-content-between align-items-center">
                      <div>
                          <i class="bi bi-file-earmark-medical me-2"></i>
                          Uploaded Medical Document Attached
                      </div>
                      <a :href="'/api/patient/view-document/' + patientHistory.patient.file" target="_blank" class="btn btn-sm btn-info text-white fw-bold">Open File</a>
                  </div>

                  <div v-if="!patientHistory?.history?.length" class="text-muted text-center py-5">
                      <i class="bi bi-clock-history fs-1 d-block mb-3 opacity-25"></i>
                      No clinical history found for this patient.
                  </div>
                  <div v-else class="list-group list-group-flush">
                      <div v-for="h in patientHistory.history" :key="h.date + h.time" class="list-group-item border-0 py-3 mb-3 bg-light rounded-3">
                          <div class="d-flex justify-content-between mb-2">
                              <span class="fw-bold text-primary">{{ h.date }} @ {{ h.time }}</span>
                              <span :class="['badge rounded-pill', statusBadgeClass(h.status)]">{{ h.status }}</span>
                          </div>
                          <p class="mb-1 fw-bold"><i class="bi bi-person-heart me-1"></i> Consulting Doctor: Dr. {{ h.doctor }}</p>
                          <div v-if="h.treatment" class="mt-2 p-2 bg-white rounded border-start border-3 border-success">
                              <p class="mb-1"><strong>Diagnosis:</strong> {{ h.treatment.diagnosis }}</p>
                              <p class="mb-1 small"><strong>Prescription:</strong> {{ h.treatment.prescription }}</p>
                              <p class="mb-0 small italic" v-if="h.treatment.notes"><strong>Notes:</strong> {{ h.treatment.notes }}</p>
                          </div>
                      </div>
                  </div>
              </div>
          </div>
      </div>
  </div>
</template>
