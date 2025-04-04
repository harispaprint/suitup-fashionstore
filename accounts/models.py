from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager

# Create your models here.

class MyAccountManger(BaseUserManager):
    def create_user(self,first_name,last_name,username,email,password=None):
        if not email:
            raise ValueError('User must have an email')
        if not username:
            raise ValueError('User must have an username')

        user = self.model(
            email = self.normalize_email(email),
            username = username,
            first_name = first_name,
            last_name = last_name,
        )
    
    #In a full implementation, you would typically also see 
    # a create_superuser method here to handle superuser creation.
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self,first_name,last_name,username,email,password):
        user = self.create_user(
            email = self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        user.is_admin = True
        user.is_active = True
        user.is_staff = True
        user.is_superadmin = True
        user.save(using=self._db)
        return user

class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=50)
    last_name  = models.CharField(max_length=50)
    username = models.CharField(max_length=50,unique=True)
    email = models.EmailField(max_length=100,unique=True)
    phone_number = models.CharField(max_length=50)

    #required
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now_add=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    objects = MyAccountManger()

    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True
    
    def status(self):
        if self.is_active:
            return 'Active'
        else:
            return 'Inactive'
        
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    address_line_1 = models.CharField(blank=True, max_length=100,default='')
    address_line_2 = models.CharField(blank=True, max_length=100,default='')
    profile_picture = models.ImageField(upload_to='userprofile',blank=True,null=True,default='userprofile/default.jpg')
    city = models.CharField(blank=True, max_length=20,default='')
    state = models.CharField(blank=True, max_length=20,default='')
    country = models.CharField(blank=True, max_length=20,default='')

    def __str__(self):
        return self.user.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
class UserAddresses(models.Model):
    user = models.ForeignKey(Account,on_delete=models.CASCADE)
    first_name = models.CharField(blank=True,max_length=100)
    last_name = models.CharField(blank=True,max_length=100)
    address_line_1 = models.CharField(blank=True, max_length=100)
    address_line_2 = models.CharField(blank=True, max_length=100)
    city = models.CharField(blank=True, max_length=20)
    state = models.CharField(blank=True, max_length=20)
    country = models.CharField(blank=True, max_length=20)
    pincode = models.CharField(max_length=6,null=True,blank=True)
    is_default = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # Check if there are any addresses for the user
        if not UserAddresses.objects.filter(user=self.user).exists():
            self.is_default = True  # Set as default if it's the first address
        super().save(*args, **kwargs)

    def __str__(self):
        return self.first_name

    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'
    
    def full_name(self):
        return f'{self.first_name} {self.last_name}'
        
# class OTP(models.Model):
#     email = models.EmailField()
#     otp = models.CharField(max_length=6)
#     created_at = models.DateTimeField(auto_now_add=True)
#     expires_at = models.DateTimeField()



