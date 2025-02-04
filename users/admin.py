from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, InfluencerProfile, SeekerProfile, UserVerification


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'username', 'user_type', 'is_verified', 'date_joined', 'is_staff')
    list_filter = ('user_type', 'is_verified', 'is_staff', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 'bio')}),
        ('Contact Info', {'fields': ('phone_number', 'location', 'website')}),
        ('Account Type', {'fields': ('user_type', 'is_verified')}),
        ('Brand Info', {'fields': ('company_name', 'industry', 'company_size')}),
        ('Influencer Info', {'fields': ('categories', 'social_links', 'audience_demographics')}),
        ('Metrics', {'fields': ('total_followers', 'average_engagement_rate')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'user_type'),
        }),
    )


@admin.register(InfluencerProfile)
class InfluencerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'primary_niche',
                    'followers', 'engagement_rate')
    search_fields = ('user__username', 'full_name', 'primary_niche')
    list_filter = ('primary_niche',)


@admin.register(SeekerProfile)
class SeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'brand_name', 'industry', 'company_size')
    search_fields = ('user__username', 'brand_name', 'industry')
    list_filter = ('industry', 'company_size')


@admin.register(UserVerification)
class UserVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'document_type', 'status', 'submitted_at', 'verified_at')
    list_filter = ('status', 'document_type', 'submitted_at')
    search_fields = ('user__email', 'user__username')
    readonly_fields = ('submitted_at',)
    
    def document_preview(self, obj):
        if obj.document_file:
            return format_html('<a href="{}" target="_blank">View Document</a>', obj.document_file.url)
        return "No document"
