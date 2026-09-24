import { Controller, Get, Post, Put, Body, Param, Req } from '@nestjs/common';
import { ReportingService } from './reporting.service';

@Controller('reporting')
export class ReportingController {
  constructor(private readonly reportingService: ReportingService) {}

  @Get('clients')
  getClients() {
    return this.reportingService.getClients();
  }

  @Post('clients')
  createClient(@Body() body: { name: string; companyName: string; logoUrl?: string; primaryColor?: string }) {
    return this.reportingService.createClient(body);
  }

  @Get('history/:clientId')
  getReportHistory(@Param('clientId') clientId: string) {
    return this.reportingService.getReportHistory(clientId);
  }

  @Post('schedule/:clientId')
  updateSchedule(
    @Param('clientId') clientId: string,
    @Body() body: { frequency: string; emailTo: string; isActive: boolean }
  ) {
    return this.reportingService.updateSchedule(clientId, body);
  }

  @Get('schedule/:clientId')
  getSchedule(@Param('clientId') clientId: string) {
    return this.reportingService.getSchedule(clientId);
  }

  @Post('generate/:clientId')
  triggerManualReport(@Param('clientId') clientId: string) {
    return this.reportingService.generateReport(clientId);
  }
}
