<template>
  <div class="fade-in">
    <!-- Hero Section -->
    <div class="row align-items-center py-5 mb-5">
      <div class="col-lg-7">
        <h1 class="display-3 fw-bold mb-4" style="line-height: 1.1;">
          Modern Healthcare <br>
          <span class="text-primary">Redefined.</span>
        </h1>
        <p class="lead text-muted mb-5 fs-4">
          Manage your health journey with a seamless, digital-first experience. 
          Expert care, instant bookings, and total transparency.
        </p>
        <div class="d-flex gap-3">
          <RouterLink to="/login" class="btn btn-primary btn-lg px-5 shadow-sm">Get Started</RouterLink>
          <RouterLink to="/register" class="btn btn-outline-primary btn-lg px-5">Join as Patient</RouterLink>
        </div>
      </div>
      <div class="col-lg-5 d-none d-lg-block">
        <div class="position-relative">
          <div class="bg-primary opacity-10 position-absolute rounded-circle" style="width: 400px; height: 400px; top: -50px; right: -50px; z-index: -1;"></div>
          <div class="card border-0 shadow-lg rounded-4 overflow-hidden">
            <div class="p-5 text-center bg-gradient-primary text-white" style="background: linear-gradient(135deg, #4f46e5, #4338ca);">
              <i class="bi bi-shield-check" style="font-size: 6rem;"></i>
              <h2 class="h1 mt-4 fw-bold">Secure <br> & Reliable</h2>
            </div>
            <div class="p-4 bg-white text-dark text-center">
              <p class="mb-0 text-muted">Trusted by thousands of healthcare professionals.</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="row g-4 py-5">
      <div class="col-md-4">
        <div class="card h-100 p-4 border-0 text-center">
          <div class="icon-box mb-3 mx-auto shadow-sm" style="width: 60px; height: 60px; line-height: 60px; border-radius: 15px; background: #eef2ff; color: #4f46e5;">
            <i class="fs-3 bi bi-calendar2-check"></i>
          </div>
          <h5 class="fw-bold">Easy Booking</h5>
          <p class="text-muted small">Schedule appointments with top specialists in seconds.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 p-4 border-0 text-center">
          <div class="icon-box mb-3 mx-auto shadow-sm" style="width: 60px; height: 60px; line-height: 60px; border-radius: 15px; background: #ecfdf5; color: #10b981;">
            <i class="fs-3 bi bi-clipboard2-pulse"></i>
          </div>
          <h5 class="fw-bold">Smart Records</h5>
          <p class="text-muted small">Access your medical history and prescriptions anywhere.</p>
        </div>
      </div>
      <div class="col-md-4">
        <div class="card h-100 p-4 border-0 text-center">
          <div class="icon-box mb-3 mx-auto shadow-sm" style="width: 60px; height: 60px; line-height: 60px; border-radius: 15px; background: #fff7ed; color: #f59e0b;">
            <i class="fs-3 bi bi-lightning-charge"></i>
          </div>
          <h5 class="fw-bold">Instant Access</h5>
          <p class="text-muted small">Connect with doctors across various specializations instantly.</p>
        </div>
      </div>
    </div>
  </div>
</template>
