"""
GraphQL schema for jobs app.
"""

import graphene
from graphene_django import DjangoObjectType
from django.db.models import Q, Exists, OuterRef, Prefetch, Value, BooleanField
from django.contrib.auth import get_user_model

from .models import Job, JobApplication, Skill, JobSkill, SavedJob
from core.schema import LocationType, CompanyType, UserType
from core.decorators import login_required, mutation_login_required

User = get_user_model()


def get_optimized_jobs_queryset(user):
    """
    Returns a base Job queryset with optimizations for related fields
    and user-specific data.
    """
    queryset = Job.objects.select_related('company', 'location').prefetch_related(
        # Prefetch JobSkill and the nested Skill to prevent N+1
        'required_skills__skill'
    )

    if user and user.is_authenticated:
        # Annotate with user-specific data if logged in
        saved_jobs_subquery = SavedJob.objects.filter(
            job_id=OuterRef('pk'),
            user=user
        )
        applications_subquery = JobApplication.objects.filter(
            job_id=OuterRef('pk'),
            user=user
        )
        queryset = queryset.annotate(
            is_saved_by_user=Exists(saved_jobs_subquery),
            is_applied_by_user=Exists(applications_subquery)
        )
    else:
        # For anonymous users, these fields are always false.
        # Annotating with a constant value is efficient.
        queryset = queryset.annotate(
            is_saved_by_user=Value(False, output_field=BooleanField()),
            is_applied_by_user=Value(False, output_field=BooleanField())
        )

    return queryset.filter(is_active=True)


class SkillType(DjangoObjectType):
    """GraphQL type for Skill model."""
    
    class Meta:
        model = Skill
        fields = (
            'id', 'name', 'slug', 'category', 'description', 
            'is_technical', 'popularity_score', 'created_at'
        )


class JobSkillType(DjangoObjectType):
    """GraphQL type for JobSkill model."""
    
    class Meta:
        model = JobSkill
        fields = ('skill', 'is_required', 'proficiency_level')


class SavedJobType(DjangoObjectType):
    """GraphQL type for the SavedJob model."""
    class Meta:
        model = SavedJob
        fields = ('id', 'user', 'job', 'saved_date')


class JobType(DjangoObjectType):
    """GraphQL type for Job model."""
    
    required_skills = graphene.List(JobSkillType)
    is_saved = graphene.Boolean()
    is_applied = graphene.Boolean()
    
    class Meta:
        model = Job
        fields = (
            'id', 'title', 'company', 'location', 'description', 
            'requirements', 'benefits', 'salary_min', 'salary_max',
            'salary_currency', 'salary_period', 'job_type', 
            'experience_level', 'remote_type', 'source', 'external_url',
            'is_active', 'posted_date', 'expires_date', 'created_at'
        )
        convert_choices_to_enum = False

    def resolve_required_skills(self, info):
        """Get required skills for this job (uses pre-fetched data)."""
        # This now uses the prefetched cache from the main resolver, making it efficient.
        return self.required_skills.all()

    def resolve_is_saved(self, info):
        """Check if job is saved by current user (uses pre-fetched annotation)."""
        # The 'is_saved_by_user' attribute is annotated in the main query resolver.
        return self.is_saved_by_user

    def resolve_is_applied(self, info):
        """Check if user has applied to this job (uses pre-fetched annotation)."""
        # The 'is_applied_by_user' attribute is annotated in the main query resolver.
        return self.is_applied_by_user


class JobApplicationType(DjangoObjectType):
    """GraphQL type for JobApplication model."""
    
    class Meta:
        model = JobApplication
        fields = (
            'id', 'user', 'job', 'status', 'applied_date', 
            'last_updated', 'cover_letter', 'notes'
        )


class JobQuery(graphene.ObjectType):
    """Job-related queries."""
    
    # Single job query
    job = graphene.Field(JobType, id=graphene.ID())
    
    # List queries
    jobs = graphene.List(
        JobType,
        # Filter arguments
        search=graphene.String(),
        location=graphene.String(), 
        company=graphene.String(),
        job_type=graphene.String(),
        experience_level=graphene.String(),
        remote_type=graphene.String(),
        limit=graphene.Int(default_value=20),
        offset=graphene.Int(default_value=0)
    )
    
    skills = graphene.List(SkillType)
    
    # User's job applications
    my_applications = graphene.List(JobApplicationType)
    
    # Map view jobs
    jobs_for_map = graphene.List(
        JobType,
        north=graphene.Float(),
        south=graphene.Float(),
        east=graphene.Float(),
        west=graphene.Float()
    )

    def resolve_job(self, info, id):
        """Get job by ID, with optimizations."""
        queryset = get_optimized_jobs_queryset(info.context.user)
        try:
            return queryset.get(pk=id)
        except Job.DoesNotExist:
            return None

    def resolve_jobs(self, info, search=None, location=None, company=None, 
                    job_type=None, experience_level=None, remote_type=None, 
                    limit=20, offset=0):
        """Get jobs with various filters and optimizations."""
        queryset = get_optimized_jobs_queryset(info.context.user)
        
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(requirements__icontains=search)
            )
        
        if location:
            queryset = queryset.filter(
                Q(location__city__icontains=location) |
                Q(location__state__icontains=location) |
                Q(location__name__icontains=location)
            )
        
        if company:
            queryset = queryset.filter(company__name__icontains=company)
        
        if job_type:
            queryset = queryset.filter(job_type=job_type)
        
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        
        if remote_type:
            queryset = queryset.filter(remote_type=remote_type)
        
        return queryset.order_by('-posted_date')[offset:offset+limit]

    def resolve_skills(self, info):
        """Get all skills."""
        return Skill.objects.all().order_by('name')

    def resolve_jobs_for_map(self, info, north=None, south=None, east=None, west=None):
        """Get jobs for map display with optional bounds filtering."""
        queryset = Job.objects.select_related('company', 'location').filter(
            is_active=True,
            location__latitude__isnull=False,
            location__longitude__isnull=False
        )
        
        # Filter by map bounds if provided
        if all([north, south, east, west]):
            queryset = queryset.filter(
                location__latitude__lte=north,
                location__latitude__gte=south,
                location__longitude__lte=east,
                location__longitude__gte=west
            )
        
        return queryset.order_by('-posted_date')

    @login_required
    def resolve_my_applications(self, info):
        """Get current user's job applications."""
        user = info.context.user
        return JobApplication.objects.filter(user=user).select_related('job__company', 'job__location').order_by('-applied_date')


class ApplyToJobMutation(graphene.Mutation):
    """Mutation to apply to a job."""
    
    class Arguments:
        job_id = graphene.ID(required=True)
        cover_letter = graphene.String()
        notes = graphene.String()

    application = graphene.Field(JobApplicationType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @mutation_login_required
    def mutate(self, info, job_id, cover_letter=None, notes=None):
        user = info.context.user

        try:
            job = Job.objects.get(pk=job_id, is_active=True)
        except Job.DoesNotExist:
            return ApplyToJobMutation(
                success=False,
                errors=['Job not found']
            )

        # Check if already applied
        if JobApplication.objects.filter(user=user, job=job).exists():
            return ApplyToJobMutation(
                success=False,
                errors=['Already applied to this job']
            )

        try:
            application = JobApplication.objects.create(
                user=user,
                job=job,
                cover_letter=cover_letter or '',
                notes=notes or ''
            )
            
            return ApplyToJobMutation(
                application=application,
                success=True,
                errors=[]
            )
        except Exception as e:
            return ApplyToJobMutation(
                success=False,
                errors=[str(e)]
            )


class UpdateApplicationStatusMutation(graphene.Mutation):
    """Mutation to update job application status."""
    
    class Arguments:
        application_id = graphene.ID(required=True)
        status = graphene.String(required=True)
        notes = graphene.String()

    application = graphene.Field(JobApplicationType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @mutation_login_required
    def mutate(self, info, application_id, status, notes=None):
        user = info.context.user

        try:
            application = JobApplication.objects.get(pk=application_id, user=user)
        except JobApplication.DoesNotExist:
            return UpdateApplicationStatusMutation(
                success=False,
                errors=['Application not found']
            )

        # Validate status
        valid_statuses = [choice[0] for choice in JobApplication._meta.get_field('status').choices]
        if status not in valid_statuses:
            return UpdateApplicationStatusMutation(
                success=False,
                errors=[f'Invalid status. Valid options: {valid_statuses}']
            )

        try:
            application.status = status
            if notes:
                application.notes = notes
            application.save()
            
            return UpdateApplicationStatusMutation(
                application=application,
                success=True,
                errors=[]
            )
        except Exception as e:
            return UpdateApplicationStatusMutation(
                success=False,
                errors=[str(e)]
            )


class SaveJobMutation(graphene.Mutation):
    """Saves a job for the current user."""
    class Arguments:
        job_id = graphene.ID(required=True)

    saved_job = graphene.Field(SavedJobType)
    success = graphene.Boolean()
    errors = graphene.List(graphene.String)

    @mutation_login_required
    def mutate(self, info, job_id):
        user = info.context.user
        try:
            job = Job.objects.get(pk=job_id, is_active=True)
        except Job.DoesNotExist:
            return SaveJobMutation(success=False, errors=['Job not found'])
        
        saved_job, created = SavedJob.objects.get_or_create(user=user, job=job)
        return SaveJobMutation(saved_job=saved_job, success=True, errors=[])


class UnsaveJobMutation(graphene.Mutation):
    """Unsaves a job for the current user."""
    class Arguments:
        job_id = graphene.ID(required=True)

    success = graphene.Boolean()
    job_id = graphene.ID()
    errors = graphene.List(graphene.String)

    @mutation_login_required
    def mutate(self, info, job_id):
        user = info.context.user
        deleted_count, _ = SavedJob.objects.filter(user=user, job_id=job_id).delete()
        return UnsaveJobMutation(success=deleted_count > 0, job_id=job_id, errors=[])


class JobMutation(graphene.ObjectType):
    """Job-related mutations."""
    
    apply_to_job = ApplyToJobMutation.Field()
    update_application_status = UpdateApplicationStatusMutation.Field()
    save_job = SaveJobMutation.Field()
    unsave_job = UnsaveJobMutation.Field()