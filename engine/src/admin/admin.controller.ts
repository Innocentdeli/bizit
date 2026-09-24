import { Controller, Get, Post, Patch, Param, Body, Query } from '@nestjs/common';
import { AdminService } from './admin.service';

@Controller('admin')
export class AdminController {
  constructor(private readonly adminService: AdminService) {}

  @Get('stats')
  getPlatformStats(@Query('adminId') adminId: string) {
    return this.adminService.getPlatformStats(adminId);
  }

  @Get('users')
  getUsers(@Query('adminId') adminId: string) {
    return this.adminService.getUsers(adminId);
  }

  @Patch('users/:id/role')
  updateUserRole(
    @Param('id') targetUserId: string,
    @Body('adminId') adminId: string,
    @Body('role') role: string,
  ) {
    return this.adminService.updateUserRole(adminId, targetUserId, role);
  }

  @Get('subscriptions')
  getSubscriptions(@Query('adminId') adminId: string) {
    return this.adminService.getSubscriptions(adminId);
  }

  @Get('logs')
  getSystemLogs(@Query('adminId') adminId: string, @Query('category') category?: string) {
    return this.adminService.getSystemLogs(adminId, category);
  }
}
